"""KNUST programme collector.

The live admissions portal is JS-heavy / often blocks simple HTTP. For Course Directory
enrichment we export undergraduate programme names already curated in
`data/knust_cutoffs_2025.json` (names only — no cut-off values are copied into the
Course Directory merge). Full HTML scrape can be added later via Playwright.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.scrape_programmes.common import (
    empty_university_payload,
    ensure_data_dir,
    programme_record,
    write_json,
)

CUTOFFS_PATH = Path(__file__).resolve().parents[2] / "data" / "knust_cutoffs_2025.json"
PORTAL_URL = "https://apps.knust.edu.gh/admissions/apply"
UNIVERSITY = "Kwame Nkrumah University of Science and Technology"
CODE = "KNUST"


def scrape_knust() -> dict[str, Any]:
    source_urls = [PORTAL_URL, str(CUTOFFS_PATH.as_posix())]
    if not CUTOFFS_PATH.exists():
        payload = empty_university_payload(
            university=UNIVERSITY,
            university_code=CODE,
            source_urls=source_urls,
            status="skipped",
            notes="KNUST cutoffs JSON missing; live portal scrape not implemented yet.",
        )
        write_json(ensure_data_dir() / "programmes_knust.json", payload)
        return payload

    try:
        raw = json.loads(CUTOFFS_PATH.read_text(encoding="utf-8"))
        rows = raw.get("programmes") or []
        programmes: list[dict[str, Any]] = []
        seen: set[str] = set()
        for row in rows:
            if not isinstance(row, dict):
                continue
            name = str(row.get("programme") or "").strip()
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            family = str(row.get("family") or "").strip()
            programmes.append(
                programme_record(
                    name=name,
                    university=UNIVERSITY,
                    university_code=CODE,
                    source_url=PORTAL_URL,
                    level="Undergraduate",
                    faculty=family,
                    overview=(
                        f"{name} is offered at KNUST (listed among undergraduate "
                        f"admission programmes). Visit the KNUST admissions portal "
                        f"for the current brochure, structure, and entry details."
                    ),
                    extra={"family": family, "name_source": "knust_cutoffs_2025.json"},
                )
            )
        payload = empty_university_payload(
            university=UNIVERSITY,
            university_code=CODE,
            source_urls=source_urls,
            status="ok" if programmes else "empty",
            notes=(
                "Programme names sourced from local KNUST cutoffs catalogue for "
                "Course Directory coverage. Cut-off points are NOT used by Course Directory."
            ),
            programmes=programmes,
        )
        write_json(ensure_data_dir() / "programmes_knust.json", payload)
        return payload
    except Exception as exc:
        payload = empty_university_payload(
            university=UNIVERSITY,
            university_code=CODE,
            source_urls=source_urls,
            status="error",
            notes=f"{type(exc).__name__}: {exc}",
        )
        write_json(ensure_data_dir() / "programmes_knust.json", payload)
        return payload


if __name__ == "__main__":
    data = scrape_knust()
    print(data["status"], data["count"], data.get("notes"))
