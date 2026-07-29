"""
Image Retrieval Service — searches repositories using ImagePlan metadata.

Never asks the LLM for URLs. Filters book covers / logos / decorative junk,
prefers high-resolution diagrams, and uses Atlas labelled SVGs when labels
are required and stock results are unreliable.

Provider cascade:
  1. Atlas labelled SVG (when requires_labels)
  2. Wikimedia Commons (full-resolution preferred)
  3. Openverse (CC aggregation; often hosts Commons/OpenStax)
  4. Wikipedia original image (not tiny thumbs when avoidable)
  5. Pixabay (optional API key)

If nothing educationally suitable is found → return None (question without image).
"""
from __future__ import annotations

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

REJECT_TITLE_RE = re.compile(
    r"(?i)\b("
    r"book\s*cover|textbook|cover\s*page|title\s*page|front\s*cover|"
    r"isbn|logo|advert|advertisement|flyer|brochure|wallpaper|"
    r"clip\s*art|clipart|stock\s*photo|poster\s*design|banner|"
    r"facebook|instagram|youtube\s*thumbnail|meme|sticker|"
    r"publisher|pearson|cambridge\s*university\s*press|oxford\s*press|"
    r"waec\s*past|exam\s*past\s*paper\s*cover"
    r")\b"
)

# Nature / scenic photos that steal keyword hits (e.g. "reflection" → lake photo)
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
    r"map|contour|punnett|circuit|organelle|cross[\s-]?section"
    r")\b"
)

POSITIVE_TITLE_RE = re.compile(
    r"(?i)\b("
    r"diagram|labelled|labeled|schematic|anatomy|structure|circuit|"
    r"map|chart|graph|figure|illustration|process|cross[\s-]?section|"
    r"osmosis|photosynthesis|cell|neuron|organ|ecosystem|mirror|ray"
    r")\b"
)

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def sanitize_attribution(raw: str | None, *, max_len: int = 160) -> str:
    """Strip HTML/markup from provider attribution for safe UI display."""
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
    blob = f"{title} {url}"
    return bool(REJECT_TITLE_RE.search(blob))


def _concept_tokens(plan: ImagePlan) -> set[str]:
    text = f"{plan.concept} {' '.join(plan.search_keywords)}"
    return {t for t in re.split(r"[^a-z0-9]+", text.lower()) if len(t) > 2}


def _score_candidate(plan: ImagePlan, candidate: dict[str, Any]) -> float:
    """Higher is better. Negative = reject."""
    title = str(candidate.get("alt") or candidate.get("title") or "")
    url = str(candidate.get("url") or "")
    if _is_rejected(title, url):
        return -100.0
    for avoid in plan.avoid:
        if avoid and avoid.lower() in title.lower():
            return -80.0

    plan_blob = f"{plan.concept} {' '.join(plan.search_keywords)} {plan.image_type}".lower()
    title_l = title.lower()
    url_l = url.lower()
    source = candidate.get("source") or ""

    # Atlas diagrams that matched topic hints are trusted
    if source == "atlas_svg":
        return 200.0

    # Scenic nature photos must never satisfy science/math diagram plans
    if SCENIC_TITLE_RE.search(title) and plan.image_type in (
        "scientific_diagram",
        "labelled_diagram",
        "graph",
        "map",
    ):
        return -100.0

    # Optics / mirror reflection: require mirror/ray terms; reject lake "reflection"
    optics = bool(
        re.search(r"(?i)\b(mirror|incident|ray\s+diagram|optics|reflection of light)\b", plan_blob)
    )
    if optics:
        if not re.search(
            r"(?i)\b(mirror|ray\s+diagram|incident|optics|normal\s+line)\b", title_l
        ):
            return -100.0
        if SCENIC_TITLE_RE.search(title) or re.search(
            r"(?i)\b(lake|mountain|landscape)\b", title_l
        ):
            return -100.0

    # Graphs / charts: title must look like a chart
    if plan.image_type == "graph" or re.search(
        r"(?i)\b(pie|bar\s*chart|histogram|number\s*line|graph)\b", plan_blob
    ):
        if not re.search(
            r"(?i)\b(chart|graph|histogram|pie|bar\s*chart|number\s*line|plot)\b", title_l
        ):
            return -100.0

    # Maps: title must mention map
    if plan.image_type == "map":
        if not re.search(r"(?i)\bmap\b", title_l):
            return -100.0

    score = 0.0
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
    }
    meaningful = {t for t in tokens if t not in filler and len(t) > 3}
    hits = sum(1 for t in meaningful if t in title_l or t in url_l)
    weak_hits = sum(1 for t in tokens if t in title_l or t in url_l)
    score += hits * 18.0

    if meaningful and hits == 0:
        return -100.0
    if len(meaningful) >= 2 and hits < 2 and weak_hits < 2:
        return -60.0

    if EDU_MARKER_RE.search(title):
        score += 25.0
    elif plan.image_type in ("scientific_diagram", "labelled_diagram", "graph"):
        score -= 30.0

    botanical = bool(
        re.search(r"(?i)\b(floral|flower|botanic|eichler|petal|stamen|ovary)\b", title)
    )
    plant_plan = bool(
        re.search(r"(?i)\b(flower|plant|botanic|petal|photosynthesis|leaf|cell)\b", plan_blob)
    )
    if botanical and not plant_plan:
        return -100.0

    if POSITIVE_TITLE_RE.search(title):
        score += 10.0
    if plan.requires_labels:
        if re.search(r"(?i)\b(label+ed|labelled|with labels)\b", title):
            score += 25.0
        else:
            score -= 10.0

    size = int(candidate.get("size") or 0)
    if size >= 200_000:
        score += 20.0
    elif size >= 80_000:
        score += 10.0
    if "thumb" in url_l and plan.requires_labels:
        score -= 25.0
    if url_l.endswith(".svg") and plan.preferred_format in ("svg", "any", "png"):
        score += 18.0 if plan.requires_labels else 8.0

    mime = str(candidate.get("mime") or "")
    if "svg" in mime and plan.requires_labels:
        score += 12.0

    return score


class ImageRetrievalService:
    """Resolve an ImagePlan to a single educational image or None."""

    async def retrieve(self, plan: ImagePlan) -> dict[str, Any] | None:
        if not getattr(settings, "EDUCATIONAL_IMAGES_ENABLED", True):
            return None
        if not plan or not plan.needed:
            return None

        cache = _load_cache()
        cache_key = f"v5|{plan.cache_key()}"
        hit = cache.get(cache_key)
        if isinstance(hit, dict) and hit.get("url"):
            # Re-validate cached entries against current reject list
            if _score_candidate(plan, hit) >= 20:
                return hit
            cache.pop(cache_key, None)

        candidates: list[dict[str, Any]] = []

        # 1) Atlas educational SVGs first (labelled cells, mirror ray diagram, charts…)
        atlas = pick_labelled_diagram(
            f"{plan.concept} {' '.join(plan.search_keywords)} {plan.primary_query()}",
            plan.subject,
        )
        if atlas:
            candidates.append(atlas)

        # 2) External providers — collect several, then score
        for query in plan.query_variants():
            for provider in (
                self._search_wikimedia,
                self._search_openverse,
                self._search_wikipedia,
                self._search_pixabay,
            ):
                try:
                    found = await provider(plan, query)
                except Exception as exc:
                    logger.info("%s failed for %r: %s", provider.__name__, query, exc)
                    continue
                if not found:
                    continue
                for item in found if isinstance(found, list) else [found]:
                    if item and item.get("url"):
                        candidates.append(item)

        scored: list[tuple[float, dict[str, Any]]] = []
        for cand in candidates:
            s = _score_candidate(plan, cand)
            if s >= 20:
                scored.append((s, cand))
        if not scored:
            logger.info(
                "No suitable educational image for concept=%r labels=%s",
                plan.concept,
                plan.requires_labels,
            )
            return None

        scored.sort(key=lambda x: x[0], reverse=True)
        best = scored[0][1]
        payload = {
            "url": best["url"],
            "alt": best.get("alt") or plan.concept or "Educational diagram",
            "attribution": sanitize_attribution(
                best.get("attribution") or best.get("source") or "Educational source"
            ),
            "source": best.get("source") or "unknown",
            "license": best.get("license") or "unknown",
            "query": plan.primary_query(),
            "concept": plan.concept,
            "requires_labels": plan.requires_labels,
            "labels": best.get("labels"),
            "key": best.get("key"),
            "chart_data": best.get("chart_data"),
            "plan": plan.to_dict(),
            "cached_at": int(time.time()),
            "size": best.get("size") or 0,
        }
        cache[cache_key] = payload
        _save_cache(cache)
        return payload

    async def _search_wikimedia(self, plan: ImagePlan, query: str) -> list[dict[str, Any]]:
        api = "https://commons.wikimedia.org/w/api.php"
        # Prefer diagrams; when labels needed, bias search terms
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
            # Request full URL + large thumb; we prefer full url for labels
            "iiprop": "url|mime|extmetadata|size",
            "iiurlwidth": 1600,
            "origin": "*",
        }
        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        async with httpx.AsyncClient(timeout=22.0, headers=headers, follow_redirects=True) as client:
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
                # Prefer original/full URL for labelled diagrams (thumbnails crop labels)
                if plan.requires_labels:
                    url = info.get("url") or info.get("thumburl")
                else:
                    url = info.get("thumburl") or info.get("url")
                if not url:
                    continue
                if _is_rejected(title, url):
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
        async with httpx.AsyncClient(timeout=22.0, headers=headers, follow_redirects=True) as client:
            res = await client.get(url, params=params)
            if res.status_code != 200:
                return []
            out: list[dict[str, Any]] = []
            for item in res.json().get("results") or []:
                title = str(item.get("title") or "")
                img = item.get("url") or item.get("thumbnail")
                if not img or _is_rejected(title, img):
                    continue
                # Prefer full url over thumbnail field when labels needed
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
                    }
                )
            return out

    async def _search_wikipedia(self, plan: ImagePlan, query: str) -> list[dict[str, Any]]:
        # Wikipedia thumbs often lose labels — skip when labels required
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
        async with httpx.AsyncClient(timeout=20.0, headers=headers, follow_redirects=True) as client:
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
            # Prefer originalimage over thumbnail
            img = (data.get("originalimage") or {}).get("source") or (data.get("thumbnail") or {}).get(
                "source"
            )
            if not img or _is_rejected(str(data.get("title") or ""), img):
                return []
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
                }
            ]

    async def _search_pixabay(self, plan: ImagePlan, query: str) -> list[dict[str, Any]]:
        key = (settings.PIXABAY_API_KEY or "").strip()
        if not key:
            return []
        # Pixabay is weaker for labelled science diagrams
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
        async with httpx.AsyncClient(timeout=20.0, headers={"User-Agent": USER_AGENT}) as client:
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
                    }
                )
            return out


# Module-level singleton for convenience
image_retrieval_service = ImageRetrievalService()


async def retrieve_for_plan(plan: ImagePlan) -> dict[str, Any] | None:
    return await image_retrieval_service.retrieve(plan)
