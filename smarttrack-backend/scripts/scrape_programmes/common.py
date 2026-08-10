"""Shared helpers for programme scrapers."""
from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "programmes"
USER_AGENT = "AtlasCourseDirectory/1.0 (+https://localhost; educational research; contact=local)"
DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
REQUEST_GAP_SECONDS = 1.0

_DEGREE_PREFIX = re.compile(
    r"^(bachelor of (science|arts|laws|education|fine arts|medicine and bachelor of surgery|"
    r"dental surgery|public health)|b\.?\s*sc\.?|b\.?\s*a\.?|b\.?\s*ed\.?|ll\.?b\.?|"
    r"mb\s*ch\.?b\.?|bds|pharm\.?d|doctor of (pharmacy|veterinary medicine|optometry)|"
    r"dvm|od)\s*(in\s+)?",
    re.I,
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return s or "programme"


def normalize_programme_key(name: str) -> str:
    """Collapse degree titles for fuzzy matching across universities."""
    s = (name or "").lower()
    s = s.replace("&", " and ")
    # Special compound degrees before generic prefix stripping
    if re.search(r"\b(mb\s*ch\.?b|bachelor of medicine)\b", s):
        return "medicine"
    if re.search(r"\b(bds|bachelor of dental surgery|dental surgery)\b", s):
        return "dental surgery"
    if re.search(r"\b(ll\.?b|bachelor of laws)\b", s):
        return "laws"
    if re.search(r"\b(pharm\.?d|doctor of pharmacy)\b", s):
        return "pharmacy"
    if re.search(r"\b(dvm|doctor of veterinary medicine|veterinary medicine)\b", s):
        return "veterinary medicine"
    s = _DEGREE_PREFIX.sub("", s)
    s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def ensure_data_dir() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def empty_university_payload(
    *,
    university: str,
    university_code: str,
    source_urls: list[str],
    status: str,
    notes: str = "",
    programmes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "university": university,
        "university_code": university_code,
        "scraped_at": utc_now_iso(),
        "status": status,
        "source_urls": source_urls,
        "notes": notes,
        "count": len(programmes or []),
        "programmes": programmes or [],
    }


def programme_record(
    *,
    name: str,
    university: str,
    university_code: str,
    source_url: str,
    level: str = "Undergraduate",
    faculty: str = "",
    department: str = "",
    duration: str = "",
    mode: str = "",
    overview: str = "",
    entry_requirements: str = "",
    core_topics: list[str] | None = None,
    career_paths: list[str] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "id": f"{university_code.lower()}-{slugify(name)}",
        "name": name.strip(),
        "normalized_name": normalize_programme_key(name),
        "university": university,
        "university_code": university_code,
        "level": level,
        "faculty": faculty.strip(),
        "department": department.strip(),
        "duration": duration.strip(),
        "mode": mode.strip(),
        "overview": overview.strip(),
        "entry_requirements": entry_requirements.strip(),
        "core_topics": core_topics or [],
        "career_paths": career_paths or [],
        "source_url": source_url.strip(),
    }
    if extra:
        row.update(extra)
    return row


class PoliteClient:
    """httpx client with robots.txt check + request spacing."""

    def __init__(self, gap: float = REQUEST_GAP_SECONDS) -> None:
        self.gap = gap
        self._last = 0.0
        self._robots: dict[str, RobotFileParser | None] = {}
        self.client = httpx.Client(headers=DEFAULT_HEADERS, follow_redirects=True, timeout=40.0)

    def close(self) -> None:
        self.client.close()

    def _wait(self) -> None:
        elapsed = time.monotonic() - self._last
        if elapsed < self.gap:
            time.sleep(self.gap - elapsed)

    def allowed(self, url: str) -> bool:
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        if origin not in self._robots:
            rp = RobotFileParser()
            robots_url = f"{origin}/robots.txt"
            try:
                self._wait()
                resp = self.client.get(robots_url)
                self._last = time.monotonic()
                if resp.status_code >= 400:
                    self._robots[origin] = None
                else:
                    rp.parse(resp.text.splitlines())
                    self._robots[origin] = rp
            except Exception:
                self._robots[origin] = None
        rp = self._robots[origin]
        if rp is None:
            return True
        return bool(rp.can_fetch(USER_AGENT, url))

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8), reraise=True)
    def get(self, url: str) -> httpx.Response:
        if not self.allowed(url):
            raise PermissionError(f"robots.txt disallows fetching {url}")
        self._wait()
        resp = self.client.get(url)
        self._last = time.monotonic()
        if resp.status_code >= 500:
            resp.raise_for_status()
        return resp
