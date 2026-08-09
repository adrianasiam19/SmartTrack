"""Educational video retrieval for Learning Center lessons.

Builds a topic-aware search query, retrieves candidate videos from YouTube
(Data API when configured, otherwise a public Invidious search fallback),
scores for educational quality, and caches results.
"""
from __future__ import annotations

import json
import logging
import re
import time
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

import httpx

from app.config import settings
from app.media.learning_resources import learning_resource

logger = logging.getLogger(__name__)

USER_AGENT = (
    "AtlasSmartTrack/1.0 (educational learning platform; "
    "https://github.com/smarttrack; contact=atlas@localhost)"
)

# Prefer recognised educational / instructional creators when ranking.
TRUSTED_CHANNEL_RE = re.compile(
    r"(?i)\b("
    r"khan\s*academy|ted[\s-]?ed|crash\s*course|organic\s*chemistry\s*tutor|"
    r"professor\s*leonard|eddie\s*woo|numberphile|3blue1brown|bozeman|"
    r"amoeba\s*sisters|ck[\s-]?12|openstax|mit\s*opencourseware|"
    r"freecodecamp|bbc|national\s*geographic|maths\s*with\s*jay|"
    r"examsolutions|corbettmaths|mathologer|veritasium|smarter\s*every\s*day|"
    r"nass\s*ss|waec|wassce|ghana\s*education|learn\s*english\s*with"
    r")\b"
)

REJECT_TITLE_RE = re.compile(
    r"(?i)\b("
    r"funny|prank|reaction|meme|music\s*video|official\s*trailer|"
    r"gameplay|asmr|vlog|comedy|tiktok|shorts\s*compilation|"
    r"unboxing|haul|gossip|drama"
    r")\b"
)

EDU_TITLE_RE = re.compile(
    r"(?i)\b("
    r"explained|explanation|tutorial|lesson|introduction|intro\s+to|"
    r"basics|beginners?|how\s+to|step\s+by\s+step|worked\s+example|"
    r"exam|wassce|waec|shs|high\s+school|gcse|class|lecture|"
    r"mathematics|maths|science|english|physics|chemistry|biology|"
    r"geography|history|grammar|algebra|matrix|matrices|calculus"
    r")\b"
)

SUBJECT_SEARCH_LABELS: dict[str, str] = {
    "core mathematics": "Mathematics",
    "core maths": "Mathematics",
    "mathematics": "Mathematics",
    "elective mathematics": "Elective Mathematics",
    "integrated science": "Integrated Science",
    "english language": "English",
    "english": "English",
    "social studies": "Social Studies",
    "biology": "Biology",
    "chemistry": "Chemistry",
    "physics": "Physics",
    "geography": "Geography",
    "economics": "Economics",
    "government": "Government",
    "history": "History",
    "ict": "ICT",
}

INVIDIOUS_INSTANCES = (
    "https://yewtu.be",
    "https://invidious.fdn.fr",
    "https://vid.puffyan.us",
)

PIPED_INSTANCES = (
    "https://pipedapi.kavin.rocks",
    "https://pipedapi.adminforge.de",
    "https://pipedapi.meuz.xyz",
)


def _cache_path() -> Path:
    raw = getattr(settings, "EDUCATIONAL_VIDEO_CACHE_PATH", "data/educational_video_cache.json")
    path = Path(raw)
    if not path.is_absolute():
        path = Path(__file__).resolve().parent.parent.parent / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _load_cache() -> dict[str, Any]:
    path = _cache_path()
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except Exception:
        return {}


def _save_cache(cache: dict[str, Any]) -> None:
    try:
        _cache_path().write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as exc:
        logger.info("Could not save video cache: %s", exc)


def _subject_label(subject: str) -> str:
    key = re.sub(r"\s+", " ", (subject or "").strip().lower())
    return SUBJECT_SEARCH_LABELS.get(key, subject.strip() or "SHS")


def build_video_queries(
    *,
    title: str,
    subject: str,
    shs_level: str | None = None,
) -> list[str]:
    """Generate ranked search queries for educational video retrieval."""
    topic = re.sub(r"\s+", " ", (title or "").strip())
    topic = re.sub(r"(?i)^(introduction|intro|unit|chapter)\s+to\s+", "", topic).strip()
    if not topic:
        topic = "curriculum topic"
    label = _subject_label(subject)
    level = (shs_level or "").strip() or "SHS"
    queries = [
        f"{level} {label} {topic}",
        f"{topic} explained for beginners",
        f"{topic} {label} tutorial",
        f"{topic} worked examples {label}",
    ]
    # Deduplicate while preserving order
    seen: set[str] = set()
    out: list[str] = []
    for q in queries:
        key = q.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(q)
    return out


def _iso_duration_to_seconds(value: str | None) -> int | None:
    if not value or not isinstance(value, str):
        return None
    m = re.fullmatch(
        r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?",
        value.strip().upper(),
    )
    if not m:
        return None
    hours = int(m.group(1) or 0)
    mins = int(m.group(2) or 0)
    secs = int(m.group(3) or 0)
    total = hours * 3600 + mins * 60 + secs
    return total if total > 0 else None


def format_duration(seconds: int | None) -> str | None:
    if seconds is None or seconds <= 0:
        return None
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def _score_video(item: dict[str, Any], query: str) -> float:
    title = str(item.get("title") or "")
    channel = str(item.get("channel") or "")
    blob = f"{title} {channel}".lower()
    score = 0.0

    if REJECT_TITLE_RE.search(title):
        return -100.0
    if TRUSTED_CHANNEL_RE.search(channel) or TRUSTED_CHANNEL_RE.search(title):
        score += 40.0
    if EDU_TITLE_RE.search(title):
        score += 18.0

    # Soft keyword overlap with the lesson query
    tokens = [t for t in re.findall(r"[a-z0-9]+", query.lower()) if len(t) > 2]
    hits = sum(1 for t in tokens if t in blob)
    score += min(20.0, hits * 2.5)

    duration = item.get("duration_seconds")
    if isinstance(duration, int):
        # Prefer short–medium instructional videos over multi-hour dumps / tiny clips
        if 90 <= duration <= 1800:
            score += 12.0
        elif duration < 45:
            score -= 15.0
        elif duration > 3600:
            score -= 8.0

    return score


async def _youtube_data_api_search(query: str, *, limit: int) -> list[dict[str, Any]]:
    api_key = (getattr(settings, "YOUTUBE_API_KEY", "") or "").strip()
    if not api_key:
        return []

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": min(max(limit * 2, 5), 12),
        "safeSearch": "strict",
        "relevanceLanguage": "en",
        "videoEmbeddable": "true",
        "key": api_key,
    }
    # Education category when available (27)
    params["videoCategoryId"] = "27"

    async with httpx.AsyncClient(timeout=10.0, headers={"User-Agent": USER_AGENT}) as client:
        res = await client.get("https://www.googleapis.com/youtube/v3/search", params=params)
        if res.status_code != 200:
            # Retry without category filter (some queries reject category+q combo)
            params.pop("videoCategoryId", None)
            res = await client.get("https://www.googleapis.com/youtube/v3/search", params=params)
            if res.status_code != 200:
                logger.warning("YouTube search HTTP %s: %s", res.status_code, res.text[:200])
                return []

        items = res.json().get("items") or []
        video_ids = [
            str((it.get("id") or {}).get("videoId") or "").strip()
            for it in items
            if (it.get("id") or {}).get("videoId")
        ]
        durations: dict[str, int] = {}
        if video_ids:
            det = await client.get(
                "https://www.googleapis.com/youtube/v3/videos",
                params={
                    "part": "contentDetails",
                    "id": ",".join(video_ids[:12]),
                    "key": api_key,
                },
            )
            if det.status_code == 200:
                for row in det.json().get("items") or []:
                    vid = str(row.get("id") or "")
                    seconds = _iso_duration_to_seconds(
                        ((row.get("contentDetails") or {}).get("duration"))
                    )
                    if vid and seconds:
                        durations[vid] = seconds

        out: list[dict[str, Any]] = []
        for it in items:
            vid = str((it.get("id") or {}).get("videoId") or "").strip()
            snip = it.get("snippet") or {}
            if not vid:
                continue
            thumbs = snip.get("thumbnails") or {}
            thumb = (
                (thumbs.get("medium") or {}).get("url")
                or (thumbs.get("high") or {}).get("url")
                or (thumbs.get("default") or {}).get("url")
            )
            out.append(
                {
                    "id": vid,
                    "title": snip.get("title") or "Educational video",
                    "channel": snip.get("channelTitle") or "YouTube",
                    "thumbnail_url": thumb,
                    "url": f"https://www.youtube.com/watch?v={vid}",
                    "description": snip.get("description") or "",
                    "duration_seconds": durations.get(vid),
                    "provider": "youtube",
                }
            )
        return out


async def _invidious_search(query: str, *, limit: int) -> list[dict[str, Any]]:
    """Key-free fallback via public Invidious instances."""
    path = f"/api/v1/search?q={quote_plus(query)}&type=video"
    async with httpx.AsyncClient(timeout=8.0, headers={"User-Agent": USER_AGENT}, follow_redirects=True) as client:
        for base in INVIDIOUS_INSTANCES:
            try:
                res = await client.get(base + path)
                if res.status_code != 200:
                    continue
                rows = res.json()
                if not isinstance(rows, list):
                    continue
                out: list[dict[str, Any]] = []
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    if (row.get("type") or "video") not in ("video",):
                        continue
                    vid = str(row.get("videoId") or "").strip()
                    if not vid:
                        continue
                    thumb = (
                        (row.get("videoThumbnails") or [{}])[0].get("url")
                        if row.get("videoThumbnails")
                        else f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
                    )
                    if isinstance(thumb, str) and thumb.startswith("//"):
                        thumb = "https:" + thumb
                    elif not thumb:
                        thumb = f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
                    out.append(
                        {
                            "id": vid,
                            "title": row.get("title") or "Educational video",
                            "channel": row.get("author") or "YouTube",
                            "thumbnail_url": thumb,
                            "url": f"https://www.youtube.com/watch?v={vid}",
                            "description": row.get("description") or "",
                            "duration_seconds": row.get("lengthSeconds"),
                            "provider": "youtube",
                        }
                    )
                    if len(out) >= limit * 2:
                        break
                if out:
                    return out
            except Exception as exc:
                logger.info("Invidious %s failed: %s", base, exc)
                continue
    return []


async def _piped_search(query: str, *, limit: int) -> list[dict[str, Any]]:
    """Key-free fallback via public Piped API instances."""
    path = f"/search?q={quote_plus(query)}&filter=videos"
    async with httpx.AsyncClient(timeout=8.0, headers={"User-Agent": USER_AGENT}, follow_redirects=True) as client:
        for base in PIPED_INSTANCES:
            try:
                res = await client.get(base + path)
                if res.status_code != 200:
                    continue
                payload = res.json()
                rows = payload.get("items") if isinstance(payload, dict) else payload
                if not isinstance(rows, list):
                    continue
                out: list[dict[str, Any]] = []
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    if (row.get("type") or "stream") not in ("stream", "video"):
                        continue
                    vid = str(row.get("url") or row.get("id") or "").strip()
                    if "/watch?v=" in vid:
                        vid = vid.split("watch?v=", 1)[-1].split("&", 1)[0]
                    vid = vid.lstrip("/")
                    if vid.startswith("watch?v="):
                        vid = vid.split("=", 1)[-1]
                    if not vid or " " in vid or len(vid) < 6:
                        # Piped often returns id field separately
                        vid = str(row.get("id") or "").strip() or vid
                    if not vid or len(vid) < 6:
                        continue
                    thumb = None
                    thumbs = row.get("thumbnail") or row.get("thumbnails")
                    if isinstance(thumbs, str):
                        thumb = thumbs
                    elif isinstance(thumbs, list) and thumbs:
                        first = thumbs[0]
                        thumb = first.get("url") if isinstance(first, dict) else str(first)
                    if isinstance(thumb, str) and thumb.startswith("//"):
                        thumb = "https:" + thumb
                    if not thumb:
                        thumb = f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
                    duration = row.get("duration")
                    if isinstance(duration, str) and ":" in duration:
                        parts = [int(p) for p in duration.split(":") if p.isdigit()]
                        if len(parts) == 3:
                            duration = parts[0] * 3600 + parts[1] * 60 + parts[2]
                        elif len(parts) == 2:
                            duration = parts[0] * 60 + parts[1]
                        else:
                            duration = None
                    out.append(
                        {
                            "id": vid,
                            "title": row.get("title") or "Educational video",
                            "channel": row.get("uploaderName") or row.get("uploader") or "YouTube",
                            "thumbnail_url": thumb,
                            "url": f"https://www.youtube.com/watch?v={vid}",
                            "description": row.get("shortDescription") or row.get("description") or "",
                            "duration_seconds": duration if isinstance(duration, int) else None,
                            "provider": "youtube",
                        }
                    )
                    if len(out) >= limit * 2:
                        break
                if out:
                    return out
            except Exception as exc:
                logger.info("Piped %s failed: %s", base, exc)
                continue
    return []


async def _search_videos(query: str, *, limit: int) -> list[dict[str, Any]]:
    found = await _youtube_data_api_search(query, limit=limit)
    if found:
        return found
    found = await _piped_search(query, limit=limit)
    if found:
        return found
    return await _invidious_search(query, limit=limit)


async def retrieve_educational_videos(
    *,
    title: str,
    subject: str,
    shs_level: str | None = None,
    limit: int = 3,
) -> dict[str, Any]:
    """
    Retrieve ranked educational video resources for a lesson topic.

    Returns {queries, resources} — never raises for optional enrichment.
    """
    if not getattr(settings, "EDUCATIONAL_VIDEOS_ENABLED", True):
        return {"queries": [], "resources": []}

    limit = max(1, min(int(limit or 3), 6))
    queries = build_video_queries(title=title, subject=subject, shs_level=shs_level)
    primary_query = queries[0] if queries else title

    cache = _load_cache()
    cache_key = f"v1|{subject}|{shs_level}|{title}|{limit}".lower()
    hit = cache.get(cache_key)
    ttl = float(getattr(settings, "EDUCATIONAL_VIDEO_CACHE_TTL_SECONDS", 86_400))
    if isinstance(hit, dict) and hit.get("resources") and (time.time() - float(hit.get("cached_at") or 0)) < ttl:
        return {"queries": hit.get("queries") or queries, "resources": hit["resources"]}

    candidates: list[dict[str, Any]] = []
    for query in queries[:2]:
        found = await _search_videos(query, limit=limit)
        for item in found:
            item = dict(item)
            item["_query"] = query
            item["_score"] = _score_video(item, query)
            if item["_score"] >= 0:
                candidates.append(item)
        if len(candidates) >= limit * 3:
            break

    # Deduplicate by video id
    best_by_id: dict[str, dict[str, Any]] = {}
    for item in candidates:
        vid = str(item.get("id") or "")
        if not vid:
            continue
        prev = best_by_id.get(vid)
        if not prev or float(item.get("_score") or 0) > float(prev.get("_score") or 0):
            best_by_id[vid] = item

    ranked = sorted(best_by_id.values(), key=lambda x: float(x.get("_score") or 0), reverse=True)
    resources: list[dict[str, Any]] = []
    for item in ranked[:limit]:
        resources.append(
            learning_resource(
                id=f"yt:{item['id']}",
                kind="video",
                title=str(item.get("title") or "Educational video"),
                url=str(item.get("url")),
                provider="youtube",
                thumbnail_url=item.get("thumbnail_url"),
                channel=item.get("channel"),
                duration_seconds=item.get("duration_seconds")
                if isinstance(item.get("duration_seconds"), int)
                else None,
                description=(str(item.get("description") or "")[:240] or None),
                query=item.get("_query") or primary_query,
                extra={"duration_label": format_duration(item.get("duration_seconds"))},
            )
        )

    # Last-resort: open a YouTube search for the lesson topic (still optional, not hardcoded links)
    if not resources:
        for idx, query in enumerate(queries[: min(limit, 2)]):
            resources.append(
                learning_resource(
                    id=f"ytsearch:{idx}:{quote_plus(query)[:40]}",
                    kind="video",
                    title=f"Find videos: {query}",
                    url=f"https://www.youtube.com/results?search_query={quote_plus(query)}",
                    provider="youtube",
                    thumbnail_url=None,
                    channel="YouTube Search",
                    duration_seconds=None,
                    description="Opens educational YouTube results for this lesson topic.",
                    query=query,
                    extra={"duration_label": None, "is_search": True},
                )
            )

    payload = {"queries": queries, "resources": resources, "cached_at": time.time()}
    cache[cache_key] = payload
    _save_cache(cache)
    return {"queries": queries, "resources": resources}
