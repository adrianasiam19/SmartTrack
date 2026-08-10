"""Merge scraped university programmes into data/course_directory.json."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.scrape_programmes.common import DATA_DIR, normalize_programme_key, utc_now_iso, write_json

COURSE_DIR_PATH = Path(__file__).resolve().parents[2] / "data" / "course_directory.json"

# Map normalized scrape keys → existing Course Directory slugs
MANUAL_ALIASES: dict[str, str] = {
    "medicine": "medicine-mbchb",
    "medicine and bachelor of surgery": "medicine-mbchb",
    "nursing": "nursing",
    "midwifery": "midwifery",
    "pharmacy": "pharmacy",
    "dental surgery": "dental-surgery",
    "medical laboratory": "medical-laboratory-science",
    "medical laboratory sciences": "medical-laboratory-science",
    "medical laboratory technology": "medical-laboratory-science",
    "physician assistantship": "physician-assistantship",
    "physiotherapy": "physiotherapy",
    "physiotherapy and sports science": "physiotherapy",
    "computer science": "computer-science",
    "information technology": "information-technology",
    "computer engineering": "computer-engineering",
    "biomedical engineering": "biomedical-engineering",
    "civil engineering": "civil-engineering",
    "mechanical engineering": "mechanical-engineering",
    "electrical engineering": "electrical-engineering",
    "chemical engineering": "chemical-engineering",
    "aerospace engineering": "aerospace-engineering",
    "petroleum engineering": "petroleum-engineering",
    "materials engineering": "materials-engineering",
    "material science and engineering": "materials-engineering",
    "actuarial science": "actuarial-science",
    "agriculture": "agriculture",
    "laws": "law-llb",
    "law": "law-llb",
    "psychology": "psychology",
    "administration": "business-administration",
    "business administration": "business-administration",
    "accounting": "accounting",
    "accounting and finance": "accounting",
    "banking and finance": "banking-finance",
    "economics": "economics",
    "business economics": "economics",
    "communication studies": "communication-studies",
    "public health": "public-health",
    "dietetics": "nutrition-dietetics",
    "nutrition and dietetics": "nutrition-dietetics",
    "veterinary medicine": "veterinary-medicine",
    "optometry": "optometry",
    "architecture": "architecture",
    "biochemistry": "biochemistry",
    "biological sciences": "biological-sciences",
    "mathematical sciences": "mathematics",
    "fine arts": "fine-art",
    "fine art": "fine-art",
    "early grade specialism": "early-childhood",
    "early childhood education": "early-childhood",
    "primary education": "education-basic",
    "basic education": "education-basic",
    "junior high school specialism": "education-secondary",
    "secondary education": "education-secondary",
    "data science and analytics": "data-science",
    "applied statistics": "statistics",
    "logistics and transport management": "supply-chain-management",
    "agribusiness": "agribusiness",
    "agribusiness and finance": "agribusiness",
    "herbal medicine": "herbal-medicine",
    "land economy": "land-economy",
    "telecommunication engineering": "telecommunications-engineering",
    "medical imaging": "medical-imaging",
    "human biology medicine": "medicine-mbchb",
}


def _load_scraped() -> list[dict[str, Any]]:
    files = [
        "programmes_ug.json",
        "programmes_knust.json",
        "programmes_ucc.json",
        "programmes_upsa.json",
    ]
    all_rows: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    for name in files:
        path = DATA_DIR / name
        if not path.exists():
            continue
        raw = json.loads(path.read_text(encoding="utf-8"))
        summaries.append(
            {
                "file": name,
                "university": raw.get("university"),
                "status": raw.get("status"),
                "count": raw.get("count"),
                "notes": raw.get("notes"),
            }
        )
        for row in raw.get("programmes") or []:
            if isinstance(row, dict) and row.get("name"):
                all_rows.append(row)
    write_json(
        DATA_DIR / "programmes_all.json",
        {
            "merged_at": utc_now_iso(),
            "sources": summaries,
            "count": len(all_rows),
            "programmes": all_rows,
        },
    )
    return all_rows


def _slug_index(programmes: list[dict[str, Any]]) -> dict[str, str]:
    """normalized key → slug from existing directory."""
    idx: dict[str, str] = dict(MANUAL_ALIASES)
    for p in programmes:
        slug = str(p.get("slug") or "")
        name = str(p.get("name") or "")
        if not slug:
            continue
        idx[normalize_programme_key(name)] = slug
        idx[normalize_programme_key(slug.replace("-", " "))] = slug
    return idx


def _best_slug(scraped: dict[str, Any], idx: dict[str, str]) -> str | None:
    key = str(scraped.get("normalized_name") or normalize_programme_key(str(scraped.get("name") or "")))
    if key in idx:
        return idx[key]
    # substring / containment pass for close titles
    for cand, slug in idx.items():
        if not cand or not key:
            continue
        if key in cand or cand in key:
            if min(len(key), len(cand)) >= 8:
                return slug
    return None


def _university_label(code: str, university: str) -> str:
    mapping = {
        "UG": "University of Ghana",
        "KNUST": "KNUST",
        "UCC": "UCC",
        "UPSA": "UPSA",
    }
    return mapping.get(code.upper(), university)


def merge_into_course_directory(*, write: bool = True) -> dict[str, Any]:
    if not COURSE_DIR_PATH.exists():
        raise FileNotFoundError(COURSE_DIR_PATH)

    directory = json.loads(COURSE_DIR_PATH.read_text(encoding="utf-8"))
    programmes: list[dict[str, Any]] = list(directory.get("programmes") or [])
    by_slug = {str(p.get("slug")): p for p in programmes if p.get("slug")}
    idx = _slug_index(programmes)
    scraped_rows = _load_scraped()

    matched = 0
    enriched_overviews = 0
    for scraped in scraped_rows:
        slug = _best_slug(scraped, idx)
        if not slug or slug not in by_slug:
            continue
        matched += 1
        target = by_slug[slug]
        uni_label = _university_label(
            str(scraped.get("university_code") or ""),
            str(scraped.get("university") or ""),
        )

        offerings = list(target.get("offerings") or [])
        source_url = str(scraped.get("source_url") or "").strip()
        overview = str(scraped.get("overview") or "").strip()
        offering = {
            "university": uni_label,
            "programme_name": scraped.get("name"),
            "overview": overview,
            "source_url": source_url,
            "department": scraped.get("department") or "",
            "duration": scraped.get("duration") or "",
            "faculty": scraped.get("faculty") or "",
        }
        # de-dupe by university + programme_name
        key = (offering["university"], str(offering["programme_name"]).lower())
        offerings = [
            o
            for o in offerings
            if (o.get("university"), str(o.get("programme_name") or "").lower()) != key
        ]
        offerings.append(offering)
        offerings.sort(key=lambda o: str(o.get("university") or ""))
        target["offerings"] = offerings

        offered_at = [str(x) for x in (target.get("commonly_offered_at") or [])]
        if uni_label not in offered_at:
            offered_at.append(uni_label)
        target["commonly_offered_at"] = offered_at

        # Prefer longer real catalogue overview for student-facing detail
        current_detail = str(target.get("detailed_overview") or "").strip()
        if overview and len(overview) >= 180 and (
            not current_detail or len(overview) > len(current_detail) + 40
        ):
            # Keep curated brief; upgrade detailed overview with university text + attribution
            target["detailed_overview"] = (
                f"{overview}\n\n"
                f"(Source: {uni_label} programme information"
                + (f" — {source_url}" if source_url else "")
                + ". Always confirm on the official university site.)"
            )
            enriched_overviews += 1

        # Collect official links
        links = list(target.get("source_urls") or [])
        if source_url and source_url not in links:
            links.append(source_url)
        target["source_urls"] = links

    directory["programmes"] = list(by_slug.values())
    directory["note"] = (
        "Course Directory for Atlas — educational programme overviews with university "
        "offerings where available. Not admission cut-offs or eligibility advice. "
        f"Last scrape merge: {utc_now_iso()}."
    )
    directory["scrape_merge"] = {
        "merged_at": utc_now_iso(),
        "scraped_rows": len(scraped_rows),
        "matched_rows": matched,
        "enriched_overviews": enriched_overviews,
    }

    if write:
        write_json(COURSE_DIR_PATH, directory)
        # Clear API lru_cache if process has it loaded (no-op for CLI)
        try:
            from app.course_directory.data import load_course_directory

            load_course_directory.cache_clear()
        except Exception:
            pass

    return directory["scrape_merge"]


if __name__ == "__main__":
    stats = merge_into_course_directory()
    print(json.dumps(stats, indent=2))
