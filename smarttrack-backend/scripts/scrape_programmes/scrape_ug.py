"""Scrape University of Ghana undergraduate programme catalogue."""
from __future__ import annotations

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

CATALOGUE_URL = "https://www.ug.edu.gh/programme-catalogue"
UNDERGRAD_TID = "18"
UNIVERSITY = "University of Ghana"
CODE = "UG"


def scrape_ug(client: PoliteClient | None = None) -> dict[str, Any]:
    own = client is None
    client = client or PoliteClient()
    try:
        url = f"{CATALOGUE_URL}?tid={UNDERGRAD_TID}&title="
        resp = client.get(url)
        if resp.status_code >= 400:
            payload = empty_university_payload(
                university=UNIVERSITY,
                university_code=CODE,
                source_urls=[CATALOGUE_URL],
                status="error",
                notes=f"HTTP {resp.status_code} from UG catalogue",
            )
            write_json(ensure_data_dir() / "programmes_ug.json", payload)
            return payload

        soup = BeautifulSoup(resp.text, "lxml")
        programmes: list[dict[str, Any]] = []
        for row in soup.select(".views-row"):
            title_a = row.select_one("a.programme-title")
            if not title_a:
                continue
            name_span = title_a.find("span")
            name = (name_span.get_text(strip=True) if name_span else title_a.get_text(strip=True)) or ""
            if not name:
                continue
            # Skip non-degree certificates when mixed in
            lower = name.lower()
            if lower.startswith("certificate"):
                continue

            dept_el = title_a.select_one(".school-department")
            department = dept_el.get_text(strip=True) if dept_el else ""
            about = row.select_one(".about-programme")
            overview = ""
            source_url = CATALOGUE_URL
            if about:
                paragraphs = about.find_all("p")
                overview = " ".join(p.get_text(" ", strip=True) for p in paragraphs).strip()
                link = about.select_one(".programme-link a[href]")
                href = (link.get("href") or "").strip() if link else ""
                if href and href not in {"#", ""}:
                    source_url = urljoin("https://www.ug.edu.gh/", href)

            programmes.append(
                programme_record(
                    name=name,
                    university=UNIVERSITY,
                    university_code=CODE,
                    source_url=source_url,
                    department=department,
                    overview=overview,
                    level="Undergraduate",
                    extra={"catalogue_url": CATALOGUE_URL},
                )
            )

        status = "ok" if programmes else "empty"
        notes = ""
        if programmes and sum(1 for p in programmes if p.get("overview")) < len(programmes) // 2:
            notes = "Some UG programme cards lack overview text on the catalogue page."

        payload = empty_university_payload(
            university=UNIVERSITY,
            university_code=CODE,
            source_urls=[CATALOGUE_URL, url],
            status=status,
            notes=notes,
            programmes=programmes,
        )
        write_json(ensure_data_dir() / "programmes_ug.json", payload)
        return payload
    except Exception as exc:
        payload = empty_university_payload(
            university=UNIVERSITY,
            university_code=CODE,
            source_urls=[CATALOGUE_URL],
            status="error",
            notes=f"{type(exc).__name__}: {exc}",
        )
        write_json(ensure_data_dir() / "programmes_ug.json", payload)
        return payload
    finally:
        if own:
            client.close()


if __name__ == "__main__":
    data = scrape_ug()
    print(data["status"], data["count"], data.get("notes"))
