"""University of Cape Coast catalogue scraper.

UCC admissions catalogue is a Livewire/JS app. This module attempts a lightweight
HTTP pass; if the page has no usable SSR content it writes a skipped stub so the
pipeline still completes. Playwright enrichment can replace this later.
"""
from __future__ import annotations

import re
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scripts.scrape_programmes.common import (
    PoliteClient,
    empty_university_payload,
    ensure_data_dir,
    programme_record,
    write_json,
)

CATALOGUE_URL = "https://admissions.ucc.edu.gh/catalogue"
UNIVERSITY = "University of Cape Coast"
CODE = "UCC"


def scrape_ucc(client: PoliteClient | None = None) -> dict[str, Any]:
    own = client is None
    client = client or PoliteClient()
    try:
        resp = client.get(CATALOGUE_URL)
        if resp.status_code >= 400:
            payload = empty_university_payload(
                university=UNIVERSITY,
                university_code=CODE,
                source_urls=[CATALOGUE_URL],
                status="error",
                notes=f"HTTP {resp.status_code}",
            )
            write_json(ensure_data_dir() / "programmes_ucc.json", payload)
            return payload

        soup = BeautifulSoup(resp.text, "lxml")
        programmes: list[dict[str, Any]] = []
        seen: set[str] = set()
        for a in soup.find_all("a", href=True):
            href = a.get("href") or ""
            if "/catalogue/programme/" not in href:
                continue
            text = re.sub(r"\s+", " ", a.get_text(" ", strip=True)).strip()
            # Card text often starts with short title then degree line
            name = text.split(" Bachelor")[0].split(" Master")[0].split(" Doctor")[0].strip()
            if not name:
                name = href.rstrip("/").split("/")[-1].replace("-", " ").title()
            key = name.lower()
            if key in seen:
                continue
            # Prefer undergraduate-looking cards from SSR snippet
            blob = text.lower()
            if any(k in blob for k in ("mphil", "msc ", "master of", "phd", "doctorate")) and not any(
                k in blob for k in ("bachelor", "bsc", "b.ed", "bcom", "pharmd", "od ")
            ):
                continue
            if not any(
                k in blob
                for k in (
                    "bachelor",
                    "bsc",
                    "b.ed",
                    "bcom",
                    "pharmd",
                    "od ",
                    "doctor of",
                )
            ):
                continue
            seen.add(key)
            source_url = urljoin(CATALOGUE_URL, href)
            programmes.append(
                programme_record(
                    name=name,
                    university=UNIVERSITY,
                    university_code=CODE,
                    source_url=source_url,
                    overview=(
                        f"{name} appears in the UCC academic programmes catalogue. "
                        f"Open the official programme page for full structure and entry information."
                    ),
                )
            )

        if programmes:
            status = "partial"
            notes = (
                "UCC catalogue is JS-rendered; only SSR/link stubs were captured. "
                "Run a Playwright pass later for full overviews."
            )
        else:
            status = "skipped"
            notes = (
                "UCC catalogue requires browser rendering (Livewire). Stub written; "
                "no SSR undergraduate rows parsed."
            )

        payload = empty_university_payload(
            university=UNIVERSITY,
            university_code=CODE,
            source_urls=[CATALOGUE_URL],
            status=status,
            notes=notes,
            programmes=programmes,
        )
        write_json(ensure_data_dir() / "programmes_ucc.json", payload)
        return payload
    except Exception as exc:
        payload = empty_university_payload(
            university=UNIVERSITY,
            university_code=CODE,
            source_urls=[CATALOGUE_URL],
            status="error",
            notes=f"{type(exc).__name__}: {exc}",
        )
        write_json(ensure_data_dir() / "programmes_ucc.json", payload)
        return payload
    finally:
        if own:
            client.close()


if __name__ == "__main__":
    data = scrape_ucc()
    print(data["status"], data["count"], data.get("notes"))
