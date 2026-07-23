"""
Educational image retrieval for Atlas.

Architecture
------------
The LLM never invents image URLs. It may propose a short `image_query`
(e.g. "plant cell diagram labelled"). Atlas resolves that query through a
provider cascade and returns a licensed educational image with attribution.

Provider order (best effort):
  1. Openverse — aggregated Creative Commons (often serves Commons files)
  2. Wikimedia Commons — direct; requires a proper User-Agent
  3. Wikipedia page image — thumbnail from related article
  4. Pixabay — optional; requires PIXABAY_API_KEY

Results are cached on disk by normalised query.
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

logger = logging.getLogger(__name__)

# Wikimedia requires a descriptive UA; generic bots get 403.
USER_AGENT = (
    "AtlasSmartTrack/1.0 (educational learning platform; "
    "https://github.com/smarttrack; contact=atlas@localhost)"
)

DIAGRAM_LANGUAGE_RE = re.compile(
    r"\b("
    r"diagram|figure|illustration|"
    r"shown\s+(below|above|here|in\s+the|on\s+the)|"
    r"activity\s+shown|image\s+shown|picture\s+shown|"
    r"study\s+the\s+(image|picture|map|graph|diagram|figure)|"
    r"look\s+at\s+the\s+(image|picture|map|graph|diagram|figure)|"
    r"the\s+(image|picture|map|graph|diagram|figure)\s+(shows|below|above)|"
    r"labelled|label\s+the|from\s+the\s+chart|in\s+the\s+graph"
    r")\b",
    re.I,
)


def mentions_visual(text: str) -> bool:
    return bool(DIAGRAM_LANGUAGE_RE.search(text or ""))


def _cache_path() -> Path:
    raw = settings.EDUCATIONAL_IMAGE_CACHE_PATH or "data/educational_image_cache.json"
    path = Path(raw)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[2] / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _norm_query(query: str) -> str:
    q = re.sub(r"\s+", " ", (query or "").strip().lower())
    return q[:160]


def _load_cache() -> dict[str, Any]:
    path = _cache_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_cache(cache: dict[str, Any]) -> None:
    path = _cache_path()
    try:
        path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as exc:
        logger.warning("Could not persist image cache: %s", exc)


def _query_variants(query: str) -> list[str]:
    """Shorter / alternate searches when a long LLM query fails."""
    base = _norm_query(query)
    if not base:
        return []
    variants = [base]
    # Drop filler words that hurt search
    cleaned = re.sub(
        r"\b(labelled|labeled|educational|simple|show(ing|s)?|the|a|an|of|in|for|and)\b",
        " ",
        base,
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if cleaned and cleaned not in variants:
        variants.append(cleaned)
    # First 3 content words
    words = [w for w in cleaned.split() if len(w) > 2][:4]
    if words:
        short = " ".join(words[:3])
        if short not in variants:
            variants.append(short)
        if f"{short} diagram" not in variants:
            variants.append(f"{short} diagram")
    # Unique preserve order
    seen: set[str] = set()
    out: list[str] = []
    for v in variants:
        if v and v not in seen:
            seen.add(v)
            out.append(v)
    return out[:6]


async def resolve_educational_image(
    query: str,
    *,
    preferred_alt: str | None = None,
) -> dict[str, Any] | None:
    """
    Resolve a search query to {url, alt, attribution, source, license, query}.
    Returns None if disabled or no suitable image found.
    """
    if not getattr(settings, "EDUCATIONAL_IMAGES_ENABLED", True):
        return None

    variants = _query_variants(query)
    if not variants:
        return None

    cache = _load_cache()
    for key in variants:
        hit = cache.get(key)
        if isinstance(hit, dict) and hit.get("url"):
            return hit

    providers = (
        _search_openverse,
        _search_wikimedia,
        _search_wikipedia_thumb,
        _search_pixabay,
    )
    for key in variants:
        for provider in providers:
            try:
                result = await provider(key)
            except Exception as exc:
                logger.info("Image provider %s failed for %r: %s", provider.__name__, key, exc)
                continue
            if result and result.get("url"):
                payload = {
                    "url": result["url"],
                    "alt": preferred_alt or result.get("alt") or key,
                    "attribution": result.get("attribution")
                    or result.get("source")
                    or "Educational source",
                    "source": result.get("source") or "unknown",
                    "license": result.get("license") or "unknown",
                    "query": key,
                    "cached_at": int(time.time()),
                }
                # Cache under all tried variants that share this concept
                cache[key] = payload
                cache[_norm_query(query)] = payload
                _save_cache(cache)
                return payload
    return None


async def _search_wikimedia(query: str) -> dict[str, Any] | None:
    """Wikimedia Commons file search — excellent labelled diagrams."""
    api = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": f"{query} filetype:bitmap|drawing",
        "gsrnamespace": 6,
        "gsrlimit": 8,
        "prop": "imageinfo",
        "iiprop": "url|mime|extmetadata|size",
        "iiurlwidth": 1280,
        "origin": "*",
    }
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    async with httpx.AsyncClient(timeout=20.0, headers=headers, follow_redirects=True) as client:
        res = await client.get(api, params=params)
        if res.status_code != 200:
            logger.info("Wikimedia HTTP %s for %r", res.status_code, query)
            return None
        pages = (res.json().get("query") or {}).get("pages") or {}
        candidates: list[dict[str, Any]] = []
        for page in pages.values():
            infos = page.get("imageinfo") or []
            if not infos:
                continue
            info = infos[0]
            mime = str(info.get("mime") or "")
            if not mime.startswith("image/"):
                continue
            url = info.get("thumburl") or info.get("url")
            if not url:
                continue
            # Prefer raster for reliable <img> rendering
            score = 0 if "svg" in mime else 10
            meta = info.get("extmetadata") or {}
            artist = (meta.get("Artist") or {}).get("value") or ""
            license_short = (meta.get("LicenseShortName") or {}).get("value") or "Commons"
            artist_clean = re.sub(r"<[^>]+>", "", artist).strip()[:120]
            candidates.append(
                {
                    "url": url,
                    "alt": page.get("title", query).replace("File:", ""),
                    "attribution": f"{artist_clean or 'Wikimedia Commons'} · {license_short}".strip(" ·"),
                    "source": "wikimedia_commons",
                    "license": license_short,
                    "size": info.get("size") or 0,
                    "score": score,
                }
            )
        if not candidates:
            return None
        candidates.sort(key=lambda c: (-c.get("score", 0), abs((c.get("size") or 0) - 400_000)))
        return candidates[0]


async def _search_openverse(query: str) -> dict[str, Any] | None:
    """Openverse CC image search (fallback aggregation)."""
    url = "https://api.openverse.org/v1/images/"
    params = {
        "q": query,
        "page_size": 8,
        "license": "cc0,pdm,by,by-sa",
    }
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    async with httpx.AsyncClient(timeout=20.0, headers=headers, follow_redirects=True) as client:
        res = await client.get(url, params=params)
        if res.status_code != 200:
            return None
        results = res.json().get("results") or []
        # Prefer non-svg / educational-looking
        ranked = sorted(
            results,
            key=lambda item: (
                0 if str(item.get("url") or "").lower().endswith(".svg") else 1,
                1 if "diagram" in str(item.get("title") or "").lower() else 0,
            ),
            reverse=True,
        )
        for item in ranked:
            img = item.get("url") or item.get("thumbnail")
            if not img:
                continue
            return {
                "url": img,
                "alt": item.get("title") or query,
                "attribution": item.get("attribution")
                or f"{item.get('creator') or 'Creator'} · {item.get('license') or 'CC'}",
                "source": "openverse",
                "license": item.get("license") or "cc",
            }
    return None


async def _search_wikipedia_thumb(query: str) -> dict[str, Any] | None:
    """Wikipedia summary thumbnail — reliable last-resort educational image."""
    title = query.replace(" diagram", "").replace(" labelled", "").strip()
    if not title:
        return None
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
            return None
        hits = (sres.json().get("query") or {}).get("search") or []
        if not hits:
            return None
        page_title = hits[0].get("title") or title
        summary = await client.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_title.replace(' ', '_')}"
        )
        if summary.status_code != 200:
            return None
        data = summary.json()
        thumb = (data.get("thumbnail") or {}).get("source") or (data.get("originalimage") or {}).get(
            "source"
        )
        if not thumb:
            return None
        return {
            "url": thumb,
            "alt": data.get("title") or query,
            "attribution": f"Wikipedia · {data.get('title') or page_title}",
            "source": "wikipedia",
            "license": "Wikipedia",
        }


async def _search_pixabay(query: str) -> dict[str, Any] | None:
    key = (settings.PIXABAY_API_KEY or "").strip()
    if not key:
        return None
    url = "https://pixabay.com/api/"
    params = {
        "key": key,
        "q": query,
        "image_type": "illustration,photo",
        "safesearch": "true",
        "per_page": 5,
    }
    async with httpx.AsyncClient(timeout=20.0, headers={"User-Agent": USER_AGENT}) as client:
        res = await client.get(url, params=params)
        if res.status_code != 200:
            return None
        hits = res.json().get("hits") or []
        if not hits:
            return None
        hit = hits[0]
        return {
            "url": hit.get("webformatURL") or hit.get("largeImageURL"),
            "alt": hit.get("tags") or query,
            "attribution": f"Pixabay / {hit.get('user') or 'contributor'}",
            "source": "pixabay",
            "license": "Pixabay License",
        }


def extract_image_query_from_text(question_text: str, subject: str = "") -> str | None:
    """Build a search query from question wording when the LLM omits image_query."""
    text = (question_text or "").strip()
    if not text:
        return subject_image_hint(subject, "") or None
    hinted = subject_image_hint(subject, text)
    if hinted:
        return hinted
    # Strip common stems and use remaining content words
    cleaned = DIAGRAM_LANGUAGE_RE.sub(" ", text)
    cleaned = re.sub(r"[^\w\s-]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    words = [w for w in cleaned.split() if len(w) > 3][:6]
    if not words:
        return None
    return " ".join(words) + " diagram"


def subject_image_hint(subject: str, question_text: str) -> str | None:
    """Lightweight keyword → search hint when the LLM omits image_query."""
    text = f"{subject} {question_text}".lower()
    pairs = [
        (("osmosis",), "osmosis diagram"),
        (("diffusion",), "diffusion diagram"),
        (("cell membrane", "plant cell", "animal cell", "organelle", "mitochondria", "nucleus"), "plant cell diagram"),
        (("heart", "circulatory", "blood vessel"), "human heart anatomy diagram"),
        (("circuit", "resistor", "ohm", "current", "voltage"), "electrical circuit diagram"),
        (("ecosystem", "food chain", "food web"), "ecosystem food web diagram"),
        (("pollution", "erosion", "environment"), "environmental pollution"),
        (("map", "latitude", "longitude", "continent", "climate"), "world map"),
        (("beaker", "flask", "apparatus", "titration"), "chemistry laboratory apparatus"),
        (("skeleton", "anatomy", "digestive", "respiratory", "lungs"), "human anatomy diagram"),
        (("photosynthesis",), "photosynthesis diagram"),
        (("periodic", "atom", "molecule", "electron"), "atomic structure diagram"),
        (("graph", "bar chart", "pie chart"), "educational bar chart"),
        (("kidney", "nephron"), "kidney nephron diagram"),
        (("flower", "pollination"), "flower structure diagram"),
        (("nervous", "neuron", "brain"), "neuron diagram"),
    ]
    for keys, hint in pairs:
        if any(k in text for k in keys):
            return hint
    return None
