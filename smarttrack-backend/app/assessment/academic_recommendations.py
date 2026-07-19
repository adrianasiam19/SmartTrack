"""
academic_recommendations.py
───────────────────────────
Academic results upload + helpers used by programme recommendations.
"""
from __future__ import annotations

import base64
import json
import logging
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.assessment.starter_arena import get_ai_response

logger = logging.getLogger(__name__)

UPLOAD_ROOT = Path(__file__).resolve().parents[2] / "uploads" / "academic"
MAX_FILE_BYTES = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp",
}


def ensure_upload_dir(user_id: str) -> Path:
    path = UPLOAD_ROOT / str(user_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def validate_academic_file(filename: str, content_type: str | None, size: int) -> str | None:
    if size <= 0:
        return "Empty file."
    if size > MAX_FILE_BYTES:
        return "That file is too large. Please choose a file under 10MB."
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return "Please choose a PDF, PNG, or JPG file."
    if content_type and content_type not in ALLOWED_CONTENT_TYPES:
        if ext not in ALLOWED_EXTENSIONS:
            return "Please choose a PDF, PNG, or JPG file."
    return None


def save_academic_file(user_id: str, filename: str, data: bytes) -> tuple[str, Path]:
    safe_name = Path(filename).name.replace(" ", "_")
    stored_name = f"{uuid.uuid4().hex[:12]}_{safe_name}"
    dest = ensure_upload_dir(user_id) / stored_name
    dest.write_bytes(data)
    return stored_name, dest


def _extract_json_object(text: str) -> dict[str, Any] | None:
    if not text:
        return None
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        data = json.loads(cleaned)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if not match:
            return None
        try:
            data = json.loads(match.group(0))
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            return None


def _normalize_grade_records(raw: Any) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    if isinstance(raw, dict):
        for subject, grade in raw.items():
            if subject and grade:
                records.append(
                    {
                        "subject": str(subject).strip()[:100],
                        "grade": str(grade).strip().upper()[:10],
                    }
                )
    elif isinstance(raw, list):
        for item in raw:
            if not isinstance(item, dict):
                continue
            subject = item.get("subject") or item.get("name")
            grade = item.get("grade") or item.get("score")
            if subject and grade:
                records.append(
                    {
                        "subject": str(subject).strip()[:100],
                        "grade": str(grade).strip().upper()[:10],
                    }
                )
    by_subject: dict[str, dict[str, str]] = {}
    for row in records:
        by_subject[row["subject"].lower()] = row
    return list(by_subject.values())


async def extract_grades_with_ai(
    *,
    filename: str,
    content_type: str | None,
    data: bytes,
) -> list[dict[str, str]]:
    """Best-effort grade extraction via LLM. Returns [] when unavailable."""
    prompt = (
        "You are helping extract WASSCE / SHS academic results from a student document.\n"
        "Return ONLY valid JSON in this shape:\n"
        '{"exam_type":"WASSCE","grades":[{"subject":"Core Mathematics","grade":"B3"}]}\n'
        "If you cannot find grades, return {\"exam_type\":\"WASSCE\",\"grades\":[]}."
    )

    is_image = (content_type or "").startswith("image/") or Path(filename).suffix.lower() in {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
    }

    if is_image:
        mime = content_type or "image/jpeg"
        b64 = base64.b64encode(data).decode("ascii")
        messages: list[dict[str, Any]] = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{b64}"},
                    },
                ],
            }
        ]
    else:
        sample = ""
        try:
            sample = data[:12000].decode("utf-8", errors="ignore")
        except Exception:
            sample = ""
        if not sample.strip():
            sample = f"(binary document named {filename}; no plain text extracted)"
        messages = [
            {
                "role": "user",
                "content": (
                    f"{prompt}\n\nFilename: {filename}\n"
                    f"Document text sample:\n{sample[:8000]}"
                ),
            }
        ]

    try:
        raw = await get_ai_response(messages)
        parsed = _extract_json_object(raw)
        if not parsed:
            return []
        return _normalize_grade_records(parsed.get("grades") or parsed.get("results") or [])
    except Exception as e:
        logger.warning(f"Grade extraction failed: {e}")
        return []


def merge_academic_upload_into_profile(
    existing_profile: dict | None,
    *,
    filename: str,
    stored_name: str,
    grades: list[dict[str, str]],
) -> dict:
    profile = dict(existing_profile or {})
    profile["academic_upload"] = {
        "filename": filename,
        "stored_name": stored_name,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "grades": grades,
        "grades_extracted": bool(grades),
    }
    return profile


def has_academic_upload(user) -> bool:
    profile = getattr(user, "learner_profile", None) or {}
    upload = profile.get("academic_upload") if isinstance(profile, dict) else None
    return bool(upload and upload.get("filename"))


def programme_fallback_skills(programme: str | None) -> dict[str, float]:
    """Synthetic skill prior when stealth IRT data is missing."""
    prog = (programme or "").lower()
    if "science" in prog:
        return {"Math": 0.6, "Science": 0.8, "Logic": 0.5, "Verbal": 0.2}
    if "art" in prog:
        return {"Math": 0.1, "Science": 0.1, "Logic": 0.4, "Verbal": 0.8}
    if "business" in prog:
        return {"Math": 0.5, "Science": 0.1, "Logic": 0.5, "Verbal": 0.6}
    return {"Math": 0.3, "Science": 0.3, "Logic": 0.4, "Verbal": 0.4}
