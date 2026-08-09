"""
Stage 3 — Intelligent Image Retrieval.

Uses Stage 2 ImagePlan search metadata (never LLM URLs).

Provider cascade (in order):
  1. Atlas labelled SVGs
  2. Wikimedia Commons
  3. Openverse
  4. Wikipedia originals
  5. Pixabay (only if PIXABAY_API_KEY exists)

Every candidate is scored for:
  educational relevance, clarity, resolution, label quality,
  image quality, and match to lesson/challenge objective.

The highest-scoring suitable image is returned.
If none pass the quality floor → None (caller generates text-only content).
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from pathlib import Path
from typing import Any

import httpx

from app.config import settings
from app.media.image_plan import ImagePlan
from app.media.labelled_diagrams import pick_labelled_diagram

logger = logging.getLogger(__name__)

USER_AGENT = (
    "AtlasSmartTrack/1.0 (educational learning platform; "
    "https://github.com/smarttrack; contact=atlas@localhost)"
)

# Minimum total score to accept an external image
SCORE_FLOOR = 20.0
# Stop searching further providers once we have a strong match
HIGH_CONFIDENCE = 75.0

REJECT_TITLE_RE = re.compile(
    r"(?i)\b("
    r"book\s*cover|textbook|cover\s*page|title\s*page|front\s*cover|"
    r"isbn|logo|advert|advertisement|flyer|brochure|wallpaper|"
    r"clip\s*art|clipart|cartoon|meme|sticker|watermark|"
    r"stock\s*photo|poster\s*design|banner|"
    r"facebook|instagram|youtube\s*thumbnail|"
    r"publisher|pearson|cambridge\s*university\s*press|oxford\s*press|"
    r"waec\s*past|exam\s*past\s*paper\s*cover"
    r")\b"
)

SCENIC_TITLE_RE = re.compile(
    r"(?i)\b("
    r"landscape|mountain|lake|sunset|sunrise|forest|waterfall|beach|"
    r"scenic|panorama|nature\s+photo|wildlife|skyline|snow[\s-]?capped|"
    r"national\s+park|tourism|vacation|holiday"
    r")\b"
)

EDU_MARKER_RE = re.compile(
    r"(?i)\b("
    r"diagram|schematic|labelled|labeled|anatomy|ray\s+diagram|"
    r"chart|graph|histogram|pie\s*chart|bar\s*chart|number\s*line|"
    r"map|contour|punnett|circuit|organelle|cross[\s-]?section|"
    r"illustration|educational|science|biology|physics|chemistry"
    r")\b"
)

POSITIVE_TITLE_RE = re.compile(
    r"(?i)\b("
    r"diagram|labelled|labeled|schematic|anatomy|structure|circuit|"
    r"map|chart|graph|figure|illustration|process|cross[\s-]?section|"
    r"osmosis|photosynthesis|cell|neuron|organ|ecosystem|mirror|ray|"
    r"pollution|digestive|apparatus|lab"
    r")\b"
)

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def sanitize_attribution(raw: str | None, *, max_len: int = 160) -> str:
    """Strip HTML/markup from provider attribution (stored internally)."""
    if not raw:
        return ""
    text = _HTML_TAG_RE.sub(" ", str(raw))
    text = text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&quot;", '"')
    text = text.replace("&#39;", "'").replace("&lt;", "<").replace("&gt;", ">")
    text = _WS_RE.sub(" ", text).strip(" ·|-")
    if len(text) > max_len:
        text = text[: max_len - 1].rstrip() + "…"
    return text


def _cache_path() -> Path:
    raw = settings.EDUCATIONAL_IMAGE_CACHE_PATH or "data/educational_image_cache.json"
    path = Path(raw)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[2] / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _load_cache() -> dict[str, Any]:
    path = _cache_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_cache(cache: dict[str, Any]) -> None:
    try:
        _cache_path().write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as exc:
        logger.warning("Image cache save failed: %s", exc)


def _is_rejected(title: str, url: str = "") -> bool:
    return bool(REJECT_TITLE_RE.search(f"{title} {url}"))


def _concept_tokens(plan: ImagePlan) -> set[str]:
    text = f"{plan.concept} {' '.join(plan.search_keywords)}"
    return {t for t in re.split(r"[^a-z0-9]+", text.lower()) if len(t) > 2}


def score_image_candidate(plan: ImagePlan, candidate: dict[str, Any]) -> dict[str, float]:
    """
    Stage 3 multi-factor scoring.

    Returns factor scores plus `total`. Negative total → reject.
    """
    title = str(candidate.get("alt") or candidate.get("title") or "")
    url = str(candidate.get("url") or "")
    title_l = title.lower()
    url_l = url.lower()
    source = str(candidate.get("source") or "")
    plan_blob = f"{plan.concept} {' '.join(plan.search_keywords)} {plan.image_type}".lower()

    factors = {
        "educational_relevance": 0.0,
        "clarity": 0.0,
        "resolution": 0.0,
        "label_quality": 0.0,
        "image_quality": 0.0,
        "objective_match": 0.0,
        "total": 0.0,
    }

    if _is_rejected(title, url):
        factors["total"] = -100.0
        return factors
    for avoid in plan.avoid:
        if avoid and avoid.lower() in title_l:
            factors["total"] = -80.0
            return factors

    # Trusted Atlas SVG that matched the topic
    if source == "atlas_svg":
        factors.update(
            {
                "educational_relevance": 40.0,
                "clarity": 35.0,
                "resolution": 30.0,
                "label_quality": 40.0 if (candidate.get("labels") or plan.requires_labels) else 20.0,
                "image_quality": 35.0,
                "objective_match": 40.0,
                "total": 200.0,
            }
        )
        return factors

    if SCENIC_TITLE_RE.search(title) and plan.image_type in (
        "scientific_diagram",
        "labelled_diagram",
        "graph",
        "chart",
        "map",
        "svg",
        "illustration",
    ):
        factors["total"] = -100.0
        return factors

    optics = bool(
        re.search(r"(?i)\b(mirror|incident|ray\s+diagram|optics|reflection of light)\b", plan_blob)
    )
    if optics:
        if not re.search(r"(?i)\b(mirror|ray\s+diagram|incident|optics|normal\s+line)\b", title_l):
            factors["total"] = -100.0
            return factors
        if SCENIC_TITLE_RE.search(title) or re.search(r"(?i)\b(lake|mountain|landscape)\b", title_l):
            factors["total"] = -100.0
            return factors

    if plan.image_type in ("graph", "chart") or re.search(
        r"(?i)\b(pie|bar\s*chart|histogram|number\s*line|graph)\b", plan_blob
    ):
        if not re.search(
            r"(?i)\b(chart|graph|histogram|pie|bar\s*chart|number\s*line|plot)\b", title_l
        ):
            factors["total"] = -100.0
            return factors

    if plan.image_type == "map" and not re.search(r"(?i)\bmap\b", title_l):
        factors["total"] = -100.0
        return factors

    botanical = bool(
        re.search(r"(?i)\b(floral|flower|botanic|eichler|petal|stamen|ovary)\b", title)
    )
    plant_plan = bool(
        re.search(r"(?i)\b(flower|plant|botanic|petal|photosynthesis|leaf|cell)\b", plan_blob)
    )
    if botanical and not plant_plan:
        factors["total"] = -100.0
        return factors

    # --- objective_match (concept / keyword overlap) ---
    tokens = _concept_tokens(plan)
    filler = {
        "diagram",
        "illustration",
        "educational",
        "labelled",
        "labeled",
        "figure",
        "image",
        "picture",
        "scene",
        "africa",
        "ghana",
        "chart",
        "map",
        "graph",
        "photo",
        "photograph",
        "real",
        "life",
        "simple",
        "light",
        "students",
        "classroom",
        "scientific",
    }
    meaningful = {t for t in tokens if t not in filler and len(t) > 3}
    hits = sum(1 for t in meaningful if t in title_l or t in url_l)
    weak_hits = sum(1 for t in tokens if t in title_l or t in url_l)
    if meaningful and hits == 0:
        factors["total"] = -100.0
        return factors
    if len(meaningful) >= 2 and hits < 2 and weak_hits < 2:
        factors["total"] = -60.0
        return factors
    factors["objective_match"] = min(40.0, hits * 14.0 + weak_hits * 2.0)

    # --- educational_relevance ---
    if EDU_MARKER_RE.search(title):
        factors["educational_relevance"] += 25.0
    elif plan.image_type in ("scientific_diagram", "labelled_diagram", "graph", "chart", "svg"):
        factors["educational_relevance"] -= 20.0
    if POSITIVE_TITLE_RE.search(title):
        factors["educational_relevance"] += 10.0
    if source in ("wikimedia_commons", "openverse", "wikipedia"):
        factors["educational_relevance"] += 6.0
    elif source == "pixabay":
        factors["educational_relevance"] += 2.0

    # --- label_quality ---
    if plan.requires_labels:
        if candidate.get("labels") or re.search(r"(?i)\b(label+ed|labelled|with labels)\b", title_l):
            factors["label_quality"] += 30.0
        else:
            factors["label_quality"] -= 12.0
        if url_l.endswith(".svg") or "svg" in str(candidate.get("mime") or "").lower():
            factors["label_quality"] += 15.0
        if "thumb" in url_l:
            factors["label_quality"] -= 20.0
    elif re.search(r"(?i)\b(label+ed|labelled)\b", title_l):
        factors["label_quality"] += 8.0

    # --- resolution ---
    size = int(candidate.get("size") or 0)
    width = int(candidate.get("width") or 0)
    height = int(candidate.get("height") or 0)
    pixels = width * height if width and height else size
    if pixels >= 800_000 or size >= 400_000:
        factors["resolution"] += 25.0
    elif pixels >= 200_000 or size >= 100_000:
        factors["resolution"] += 15.0
    elif pixels >= 80_000 or size >= 40_000:
        factors["resolution"] += 8.0
    elif "thumb" in url_l:
        factors["resolution"] -= 10.0

    # --- clarity / image_quality ---
    if url_l.endswith(".svg") or "svg" in str(candidate.get("mime") or "").lower():
        factors["clarity"] += 18.0
        factors["image_quality"] += 15.0
    if EDU_MARKER_RE.search(title) and not SCENIC_TITLE_RE.search(title):
        factors["clarity"] += 12.0
    if re.search(r"(?i)\b(blurry|low[\s-]?res|pixelated|noisy)\b", title_l):
        factors["clarity"] -= 25.0
        factors["image_quality"] -= 25.0
    if plan.image_type == "photograph" and source == "pixabay":
        factors["image_quality"] += 8.0
    if plan.preferred_format == "svg" and (
        url_l.endswith(".svg") or "svg" in str(candidate.get("mime") or "").lower()
    ):
        factors["image_quality"] += 10.0

    factors["total"] = (
        factors["educational_relevance"]
        + factors["clarity"]
        + factors["resolution"]
        + factors["label_quality"]
        + factors["image_quality"]
        + factors["objective_match"]
    )
    return factors


def _score_candidate(plan: ImagePlan, candidate: dict[str, Any]) -> float:
    """Back-compat wrapper used by cache revalidation."""
    return float(score_image_candidate(plan, candidate)["total"])


class ImageRetrievalService:
    """Resolve an ImagePlan to the highest-scoring educational image or None."""

    async def retrieve(self, plan: ImagePlan) -> dict[str, Any] | None:
        if not getattr(settings, "EDUCATIONAL_IMAGES_ENABLED", True):
            return None
        if not plan or not plan.needed:
            return None

        cache = _load_cache()
        cache_key = f"v6|{plan.cache_key()}"
        hit = cache.get(cache_key)
        if isinstance(hit, dict) and hit.get("url"):
            if _score_candidate(plan, hit) >= SCORE_FLOOR:
                return hit
            cache.pop(cache_key, None)

        candidates: list[dict[str, Any]] = []
        queries = list(plan.query_variants())[:3] or [plan.primary_query()]
        queries = [q for q in queries if q]
        if not queries:
            return None

        # 1) Atlas labelled SVGs first
        atlas = pick_labelled_diagram(
            f"{plan.concept} {' '.join(plan.search_keywords)} {plan.primary_query()}",
            plan.subject,
        )
        if atlas:
            candidates.append(atlas)
            atlas_score = _score_candidate(plan, atlas)
            if plan.requires_labels or atlas_score >= HIGH_CONFIDENCE:
                logger.info(
                    "Image retrieval chose Atlas SVG concept=%r score=%.1f",
                    plan.concept,
                    atlas_score,
                )
                return self._finalize(plan, cache, cache_key, candidates)

        # 2–5) External providers in cascade order
        provider_steps = (
            ("wikimedia_commons", self._search_wikimedia),
            ("openverse", self._search_openverse),
            ("wikipedia", self._search_wikipedia),
            ("pixabay", self._search_pixabay),
        )

        for provider_name, provider in provider_steps:
            # Search top Stage-2 phrases in parallel for this provider
            tasks = [provider(plan, query) for query in queries]
            try:
                results = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=8.0,
                )
            except asyncio.TimeoutError:
                logger.info(
                    "Image provider timed out: %s concept=%r",
                    provider_name,
                    plan.concept,
                )
                results = []

            added = 0
            for found in results:
                if isinstance(found, Exception) or not found:
                    continue
                for item in found if isinstance(found, list) else [found]:
                    if item and item.get("url"):
                        candidates.append(item)
                        added += 1

            if added:
                best_so_far = self._best_scored(plan, candidates)
                if best_so_far and best_so_far[0] >= HIGH_CONFIDENCE:
                    logger.info(
                        "Image retrieval early-stop after %s concept=%r score=%.1f",
                        provider_name,
                        plan.concept,
                        best_so_far[0],
                    )
                    return self._finalize(plan, cache, cache_key, candidates)

        return self._finalize(plan, cache, cache_key, candidates)

    async def retrieve_local_only(self, plan: ImagePlan) -> dict[str, Any] | None:
        """
        Option B — free images only (no network).

        Order: Atlas labelled SVG → existing educational_image_cache hit.
        Never calls Wikimedia / Openverse / Wikipedia / Pixabay.
        Safe to use on the Start / prefetch critical path.
        """
        if not getattr(settings, "EDUCATIONAL_IMAGES_ENABLED", True):
            return None
        if not plan or not plan.needed:
            return None

        # 1) Atlas SVG (instant, reliable labels)
        atlas = pick_labelled_diagram(
            f"{plan.concept} {' '.join(plan.search_keywords)} {plan.primary_query()}",
            plan.subject,
        )
        if atlas and atlas.get("url"):
            logger.info(
                "Challenge image local_only Atlas SVG concept=%r key=%s",
                plan.concept,
                atlas.get("key"),
            )
            return atlas

        # 2) Existing cache only (no write / no fetch)
        cache = _load_cache()
        cache_key = f"v6|{plan.cache_key()}"
        hit = cache.get(cache_key)
        if isinstance(hit, dict) and hit.get("url"):
            # Prefer educational-looking cached diagrams; skip weak matches.
            if _score_candidate(plan, hit) >= SCORE_FLOOR:
                # Prefer diagram-like sources; still allow if score is high enough.
                logger.info(
                    "Challenge image local_only cache hit concept=%r",
                    plan.concept,
                )
                return hit

        # Also try a few query strings as cache keys (older cache format).
        for q in list(plan.query_variants())[:4]:
            raw = cache.get(q) or cache.get((q or "").lower())
            if isinstance(raw, dict) and raw.get("url"):
                if _score_candidate(plan, raw) >= SCORE_FLOOR:
                    logger.info(
                        "Challenge image local_only legacy cache key=%r",
                        q,
                    )
                    return raw

        return None

    def _best_scored(
        self, plan: ImagePlan, candidates: list[dict[str, Any]]
    ) -> tuple[float, dict[str, Any], dict[str, float]] | None:
        best: tuple[float, dict[str, Any], dict[str, float]] | None = None
        for cand in candidates:
            factors = score_image_candidate(plan, cand)
            total = float(factors["total"])
            if total < SCORE_FLOOR:
                continue
            if best is None or total > best[0]:
                best = (total, cand, factors)
        return best

    def _finalize(
        self,
        plan: ImagePlan,
        cache: dict[str, Any],
        cache_key: str,
        candidates: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        best = self._best_scored(plan, candidates)
        if not best:
            logger.info(
                "No suitable educational image for concept=%r labels=%s candidates=%s",
                plan.concept,
                plan.requires_labels,
                len(candidates),
            )
            return None

        total, winner, factors = best
        payload = {
            "url": winner["url"],
            "alt": winner.get("alt") or plan.concept or "Educational diagram",
            "attribution": sanitize_attribution(
                winner.get("attribution") or winner.get("source") or "Educational source"
            ),
            "source": winner.get("source") or "unknown",
            "license": winner.get("license") or "unknown",
            "query": plan.primary_query(),
            "queries_used": list(plan.query_variants())[:3],
            "concept": plan.concept,
            "requires_labels": plan.requires_labels,
            "labels": winner.get("labels"),
            "key": winner.get("key"),
            "chart_data": winner.get("chart_data"),
            "plan": plan.to_dict(),
            "score": round(total, 2),
            "score_factors": {k: round(float(v), 2) for k, v in factors.items()},
            "cached_at": int(time.time()),
            "size": int(winner.get("size") or 0),
        }
        cache[cache_key] = payload
        _save_cache(cache)
        logger.info(
            "Image retrieval selected source=%s concept=%r score=%.1f factors=%s",
            payload["source"],
            plan.concept,
            total,
            {k: payload["score_factors"][k] for k in (
                "educational_relevance",
                "clarity",
                "resolution",
                "label_quality",
                "image_quality",
                "objective_match",
            )},
        )
        return payload

    async def _search_wikimedia(self, plan: ImagePlan, query: str) -> list[dict[str, Any]]:
        api = "https://commons.wikimedia.org/w/api.php"
        search = query
        if plan.requires_labels and "label" not in query.lower():
            search = f"labelled OR labeled {query} diagram"
        params = {
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": search,
            "gsrnamespace": 6,
            "gsrlimit": 12,
            "prop": "imageinfo",
            "iiprop": "url|mime|extmetadata|size",
            "iiurlwidth": 1600,
            "origin": "*",
        }
        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        async with httpx.AsyncClient(timeout=8.0, headers=headers, follow_redirects=True) as client:
            res = await client.get(api, params=params)
            if res.status_code != 200:
                return []
            pages = (res.json().get("query") or {}).get("pages") or {}
            out: list[dict[str, Any]] = []
            for page in pages.values():
                infos = page.get("imageinfo") or []
                if not infos:
                    continue
                info = infos[0]
                mime = str(info.get("mime") or "")
                if not mime.startswith("image/"):
                    continue
                title = str(page.get("title") or "").replace("File:", "")
                if plan.requires_labels:
                    url = info.get("url") or info.get("thumburl")
                else:
                    url = info.get("thumburl") or info.get("url")
                if not url or _is_rejected(title, url):
                    continue
                meta = info.get("extmetadata") or {}
                artist = re.sub(
                    r"<[^>]+>",
                    "",
                    (meta.get("Artist") or {}).get("value") or "",
                ).strip()[:120]
                license_short = (meta.get("LicenseShortName") or {}).get("value") or "Commons"
                out.append(
                    {
                        "url": url,
                        "alt": title,
                        "attribution": sanitize_attribution(
                            f"{artist or 'Wikimedia Commons'} · {license_short}"
                        ),
                        "source": "wikimedia_commons",
                        "license": license_short,
                        "size": int(info.get("size") or 0),
                        "width": int(info.get("width") or 0),
                        "height": int(info.get("height") or 0),
                        "mime": mime,
                    }
                )
            return out

    async def _search_openverse(self, plan: ImagePlan, query: str) -> list[dict[str, Any]]:
        url = "https://api.openverse.org/v1/images/"
        params = {
            "q": query,
            "page_size": 12,
            "license": "cc0,pdm,by,by-sa",
        }
        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        async with httpx.AsyncClient(timeout=8.0, headers=headers, follow_redirects=True) as client:
            res = await client.get(url, params=params)
            if res.status_code != 200:
                return []
            out: list[dict[str, Any]] = []
            for item in res.json().get("results") or []:
                title = str(item.get("title") or "")
                img = item.get("url") or item.get("thumbnail")
                if not img or _is_rejected(title, img):
                    continue
                if plan.requires_labels and item.get("url"):
                    img = item["url"]
                out.append(
                    {
                        "url": img,
                        "alt": title or query,
                        "attribution": sanitize_attribution(
                            item.get("attribution")
                            or f"{item.get('creator') or 'Creator'} · {item.get('license') or 'CC'}"
                        ),
                        "source": "openverse",
                        "license": item.get("license") or "cc",
                        "size": int(item.get("filesize") or 0),
                        "width": int(item.get("width") or 0),
                        "height": int(item.get("height") or 0),
                    }
                )
            return out

    async def _search_wikipedia(self, plan: ImagePlan, query: str) -> list[dict[str, Any]]:
        if plan.requires_labels:
            return []
        title = re.sub(r"\b(diagram|labelled|labeled)\b", " ", query, flags=re.I)
        title = re.sub(r"\s+", " ", title).strip()
        if not title:
            return []
        search_api = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": title,
            "srlimit": 1,
            "format": "json",
            "origin": "*",
        }
        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        async with httpx.AsyncClient(timeout=8.0, headers=headers, follow_redirects=True) as client:
            sres = await client.get(search_api, params=params)
            if sres.status_code != 200:
                return []
            hits = (sres.json().get("query") or {}).get("search") or []
            if not hits:
                return []
            page_title = hits[0].get("title") or title
            summary = await client.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_title.replace(' ', '_')}"
            )
            if summary.status_code != 200:
                return []
            data = summary.json()
            img = (data.get("originalimage") or {}).get("source") or (
                data.get("thumbnail") or {}
            ).get("source")
            if not img or _is_rejected(str(data.get("title") or ""), img):
                return []
            original = data.get("originalimage") or {}
            return [
                {
                    "url": img,
                    "alt": data.get("title") or query,
                    "attribution": sanitize_attribution(
                        f"Wikipedia · {data.get('title') or page_title}"
                    ),
                    "source": "wikipedia",
                    "license": "Wikipedia",
                    "size": 0,
                    "width": int(original.get("width") or 0),
                    "height": int(original.get("height") or 0),
                }
            ]

    async def _search_pixabay(self, plan: ImagePlan, query: str) -> list[dict[str, Any]]:
        key = (settings.PIXABAY_API_KEY or "").strip()
        if not key:
            return []
        if plan.requires_labels:
            return []
        url = "https://pixabay.com/api/"
        params = {
            "key": key,
            "q": query,
            "image_type": "illustration,photo",
            "safesearch": "true",
            "per_page": 8,
        }
        async with httpx.AsyncClient(timeout=8.0, headers={"User-Agent": USER_AGENT}) as client:
            res = await client.get(url, params=params)
            if res.status_code != 200:
                return []
            out: list[dict[str, Any]] = []
            for hit in res.json().get("hits") or []:
                title = str(hit.get("tags") or "")
                img = hit.get("largeImageURL") or hit.get("webformatURL")
                if not img or _is_rejected(title, img):
                    continue
                out.append(
                    {
                        "url": img,
                        "alt": title or query,
                        "attribution": sanitize_attribution(
                            f"Pixabay / {hit.get('user') or 'contributor'}"
                        ),
                        "source": "pixabay",
                        "license": "Pixabay License",
                        "size": int(hit.get("imageWidth") or 0) * int(hit.get("imageHeight") or 0),
                        "width": int(hit.get("imageWidth") or 0),
                        "height": int(hit.get("imageHeight") or 0),
                    }
                )
            return out


image_retrieval_service = ImageRetrievalService()


async def retrieve_for_plan(plan: ImagePlan) -> dict[str, Any] | None:
    return await image_retrieval_service.retrieve(plan)


async def retrieve_for_plan_local_only(plan: ImagePlan) -> dict[str, Any] | None:
    """Challenge Option B: SVG / cache only — never blocks on live search."""
    return await image_retrieval_service.retrieve_local_only(plan)
