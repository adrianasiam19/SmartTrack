"""Scrape UPSA undergraduate programme list."""
from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup

from scripts.scrape_programmes.common import (
    PoliteClient,
    empty_university_payload,
    ensure_data_dir,
    programme_record,
    write_json,
)

SOURCE_URL = (
    "https://admissions.upsa.edu.gh/admissions/undergraduate/undergraduate-programmes/"
)
UNIVERSITY = "University of Professional Studies, Accra"
CODE = "UPSA"
_NAME_RE = re.compile(
    r"^(Bachelor of .+|Diploma in .+)$",
    re.I,
)


def scrape_upsa(client: PoliteClient | None = None) -> dict[str, Any]:
    own = client is None
    client = client or PoliteClient()
    try:
        resp = client.get(SOURCE_URL)
        if resp.status_code >= 400:
            payload = empty_university_payload(
                university=UNIVERSITY,
                university_code=CODE,
                source_urls=[SOURCE_URL],
                status="error",
                notes=f"HTTP {resp.status_code}",
            )
            write_json(ensure_data_dir() / "programmes_upsa.json", payload)
            return payload

        soup = BeautifulSoup(resp.text, "lxml")
        main = soup.find("main") or soup.find(class_="entry-content") or soup.body
        text = main.get_text("\n", strip=True) if main else ""
        programmes: list[dict[str, Any]] = []
        seen: set[str] = set()
        for line in text.splitlines():
            name = line.strip()
            if not _NAME_RE.match(name):
                continue
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            level = "Diploma" if name.lower().startswith("diploma") else "Undergraduate"
            programmes.append(
                programme_record(
                    name=name,
                    university=UNIVERSITY,
                    university_code=CODE,
                    source_url=SOURCE_URL,
                    level=level,
                    overview=(
                        f"{name} is listed among UPSA undergraduate/diploma offerings "
                        f"on the official admissions programmes page. Confirm current "
                        f"curriculum details on the university site."
                    ),
                )
            )

        # Prefer undergraduate degree rows for Course Directory merge; keep diplomas too.
        status = "ok" if programmes else "empty"
        payload = empty_university_payload(
            university=UNIVERSITY,
            university_code=CODE,
            source_urls=[SOURCE_URL],
            status=status,
            notes="UPSA page lists programme names; detailed curriculum text is limited.",
            programmes=programmes,
        )
        write_json(ensure_data_dir() / "programmes_upsa.json", payload)
        return payload
    except Exception as exc:
        payload = empty_university_payload(
            university=UNIVERSITY,
            university_code=CODE,
            source_urls=[SOURCE_URL],
            status="error",
            notes=f"{type(exc).__name__}: {exc}",
        )
        write_json(ensure_data_dir() / "programmes_upsa.json", payload)
        return payload
    finally:
        if own:
            client.close()


if __name__ == "__main__":
    data = scrape_upsa()
    print(data["status"], data["count"], data.get("notes"))
