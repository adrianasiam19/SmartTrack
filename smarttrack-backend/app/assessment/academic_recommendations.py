"""
academic_recommendations.py
───────────────────────────
Academic results upload + grade extraction.

PDFs are parsed with pypdf (text extraction + WASSCE grade regex).
Images still use best-effort LLM vision when available.
"""
from __future__ import annotations

import base64
import io
import json
import logging
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pypdf import PdfReader

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

VALID_GRADES = {
    "A1",
    "A",
    "B2",
    "B3",
    "B",
    "C4",
    "C5",
    "C6",
    "C",
    "D7",
    "D",
    "E8",
    "E",
    "F9",
    "F",
}

# Common WASSCE / SHS subject labels (matched case-insensitively).
KNOWN_SUBJECTS = [
    "English Language",
    "English",
    "Core Mathematics",
    "Mathematics (Core)",
    "Mathematics Core",
    "Core Maths",
    "Integrated Science",
    "Social Studies",
    "Elective Mathematics",
    "Mathematics (Elective)",
    "Additional Mathematics",
    "Further Mathematics",
    "Physics",
    "Chemistry",
    "Biology",
    "Geography",
    "Economics",
    "Accounting",
    "Business Management",
    "Principles of Costing",
    "Financial Accounting",
    "Government",
    "History",
    "Literature in English",
    "Literature",
    "French",
    "Christian Religious Studies",
    "Islamic Religious Studies",
    "Religious Studies",
    "Agriculture",
    "Agricultural Science",
    "Animal Husbandry",
    "Crop Husbandry",
    "Food and Nutrition",
    "Management in Living",
    "Clothing and Textiles",
    "Information and Communication Technology",
    "ICT",
    "Computer Studies",
    "Technical Drawing",
    "Building Construction",
    "Woodwork",
    "Metalwork",
    "Applied Electricity",
    "Electronics",
    "Graphic Design",
    "Visual Arts",
    "General Knowledge in Art",
    "Music",
    "Physical Education",
]

# Prefer multi-char WAEC codes first so "B3" is not split as "B".
_GRADE_TOKEN = r"(?:A1|B2|B3|C4|C5|C6|D7|E8|F9|A|B|C|D|E|F)\b"
_SUBJECT_ALT = "|".join(
    sorted((re.escape(s) for s in KNOWN_SUBJECTS), key=len, reverse=True)
)


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


def extract_text_from_pdf(data: bytes) -> str:
    """Extract plain text from a PDF using pypdf."""
    try:
        reader = PdfReader(io.BytesIO(data))
        parts: list[str] = []
        for page in reader.pages:
            text = page.extract_text() or ""
            if text.strip():
                parts.append(text)
        return "\n".join(parts).strip()
    except Exception as e:
        logger.warning("pypdf failed to read PDF: %s", e)
        return ""


def _canonical_subject(raw: str) -> str:
    cleaned = re.sub(r"\s+", " ", raw.strip(" :-|\t"))
    lower = cleaned.lower()
    for name in KNOWN_SUBJECTS:
        if name.lower() == lower:
            return name
    # Light normalizations
    if "math" in lower and "elect" in lower:
        return "Elective Mathematics"
    if "math" in lower and ("core" in lower or lower in {"mathematics", "maths", "math"}):
        return "Core Mathematics"
    if "english" in lower:
        return "English Language"
    if "integrated science" in lower or lower == "science":
        return "Integrated Science"
    if "social" in lower:
        return "Social Studies"
    return cleaned.title()[:100]


def _normalize_grade(raw: str) -> str | None:
    g = str(raw or "").strip().upper().replace(" ", "")
    # Allow forms like "GRADE:B3" already stripped
    if g in VALID_GRADES:
        # Prefer WAEC letter+digit when letter-only also valid
        return g
    m = re.fullmatch(r"(A1|B2|B3|C4|C5|C6|D7|E8|F9|[A-F])", g)
    if m:
        return m.group(1)
    return None


def parse_grades_from_text(text: str) -> list[dict[str, str]]:
    """
    Parse subject/grade pairs from WASSCE-style PDF text.

    Handles patterns such as:
      Core Mathematics .......... B3
      Mathematics (Core) A1
      English Language: C4
      PHYSICS - B2
    """
    if not text or not text.strip():
        return []

    # Keep line structure; strip dotted leaders like "........"
    lines = [re.sub(r"[.\u2026]{2,}", " ", ln).strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]

    found: dict[str, dict[str, str]] = {}

    def _add(subject: str, grade: str) -> None:
        norm_grade = _normalize_grade(grade)
        if not norm_grade:
            return
        subject_name = _canonical_subject(subject)
        if len(subject_name) < 3:
            return
        # Skip header junk
        low = subject_name.lower()
        if any(
            bad in low
            for bad in (
                "candidate",
                "centre",
                "index",
                "exam",
                "result",
                "grade",
                "subject",
                "wassce",
                "waec",
                "page",
            )
        ):
            return
        key = subject_name.lower()
        # Prefer more specific WAEC codes (B3 over B)
        prev = found.get(key)
        if prev and len(prev["grade"]) > len(norm_grade):
            return
        found[key] = {"subject": subject_name, "grade": norm_grade}

    # 1) Known subjects followed by a grade (same line only)
    known_pat = re.compile(
        rf"(?P<subject>{_SUBJECT_ALT})\s*[:\-]?\s*(?P<grade>{_GRADE_TOKEN})",
        re.IGNORECASE,
    )
    # 2) Generic "Some Subject Name .... A1" per line
    line_pat = re.compile(
        rf"^(?P<subject>[A-Za-z][A-Za-z0-9 /()&-]{{2,80}}?)\s*[:\-]?\s*(?P<grade>{_GRADE_TOKEN})\s*$",
        re.IGNORECASE,
    )
    # 3) Table-ish: SUBJECT GRADE with extra spaces
    spaced_pat = re.compile(
        rf"(?P<subject>{_SUBJECT_ALT})\s{{2,}}(?P<grade>{_GRADE_TOKEN})",
        re.IGNORECASE,
    )
    # 4) Grade then subject on the same line only (rare)
    reverse_pat = re.compile(
        rf"^(?P<grade>{_GRADE_TOKEN})\s+[:\-]?\s*(?P<subject>{_SUBJECT_ALT})\s*$",
        re.IGNORECASE,
    )

    for ln in lines:
        for m in known_pat.finditer(ln):
            _add(m.group("subject"), m.group("grade"))
        m = line_pat.match(ln.strip())
        if m:
            _add(m.group("subject"), m.group("grade"))
        for m in spaced_pat.finditer(ln):
            _add(m.group("subject"), m.group("grade"))
        m = reverse_pat.match(ln.strip())
        if m:
            _add(m.group("subject"), m.group("grade"))

    return list(found.values())


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
            norm = _normalize_grade(str(grade))
            if subject and norm:
                records.append(
                    {
                        "subject": _canonical_subject(str(subject)),
                        "grade": norm,
                    }
                )
    elif isinstance(raw, list):
        for item in raw:
            if not isinstance(item, dict):
                continue
            subject = item.get("subject") or item.get("name")
            grade = item.get("grade") or item.get("score")
            norm = _normalize_grade(str(grade)) if grade else None
            if subject and norm:
                records.append(
                    {
                        "subject": _canonical_subject(str(subject)),
                        "grade": norm,
                    }
                )
    by_subject: dict[str, dict[str, str]] = {}
    for row in records:
        by_subject[row["subject"].lower()] = row
    return list(by_subject.values())


async def _extract_grades_with_ai_from_text(text: str, filename: str) -> list[dict[str, str]]:
    prompt = (
        "You are helping extract WASSCE / SHS academic results from document text.\n"
        "Return ONLY valid JSON in this shape:\n"
        '{"exam_type":"WASSCE","grades":[{"subject":"Core Mathematics","grade":"B3"}]}\n'
        "If you cannot find grades, return {\"exam_type\":\"WASSCE\",\"grades\":[]}."
    )
    messages = [
        {
            "role": "user",
            "content": (
                f"{prompt}\n\nFilename: {filename}\n"
                f"Document text:\n{text[:12000]}"
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
        logger.warning("AI grade extraction from text failed: %s", e)
        return []


async def _extract_grades_from_image(
    *,
    filename: str,
    content_type: str | None,
    data: bytes,
) -> list[dict[str, str]]:
    prompt = (
        "You are helping extract WASSCE / SHS academic results from a student document.\n"
        "Return ONLY valid JSON in this shape:\n"
        '{"exam_type":"WASSCE","grades":[{"subject":"Core Mathematics","grade":"B3"}]}\n'
        "If you cannot find grades, return {\"exam_type\":\"WASSCE\",\"grades\":[]}."
    )
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
    try:
        raw = await get_ai_response(messages)
        parsed = _extract_json_object(raw)
        if not parsed:
            return []
        return _normalize_grade_records(parsed.get("grades") or parsed.get("results") or [])
    except Exception as e:
        logger.warning("Image grade extraction failed: %s", e)
        return []


async def extract_grades_with_ai(
    *,
    filename: str,
    content_type: str | None,
    data: bytes,
) -> list[dict[str, str]]:
    """
    Extract subject grades from an uploaded academic document.

    PDFs: pypdf text extraction → regex parse (primary); AI on extracted text as fallback.
    Images: LLM vision best-effort.
    """
    ext = Path(filename).suffix.lower()
    is_pdf = ext == ".pdf" or (content_type or "").lower() == "application/pdf"
    is_image = (content_type or "").startswith("image/") or ext in {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
    }

    if is_pdf:
        pdf_text = extract_text_from_pdf(data)
        if not pdf_text:
            logger.warning(
                "pypdf extracted no text from %s (may be a scanned/image-only PDF)",
                filename,
            )
            return []

        grades = parse_grades_from_text(pdf_text)
        if grades:
            logger.info(
                "Parsed %s grade(s) from PDF via pypdf for %s",
                len(grades),
                filename,
            )
            return grades

        logger.info(
            "pypdf text found but regex miss for %s; trying AI on extracted text",
            filename,
        )
        return await _extract_grades_with_ai_from_text(pdf_text, filename)

    if is_image:
        return await _extract_grades_from_image(
            filename=filename,
            content_type=content_type,
            data=data,
        )

    # Unknown binary: try pypdf then plain decode
    pdf_text = extract_text_from_pdf(data)
    if pdf_text:
        grades = parse_grades_from_text(pdf_text)
        if grades:
            return grades
        return await _extract_grades_with_ai_from_text(pdf_text, filename)

    sample = data[:12000].decode("utf-8", errors="ignore")
    if sample.strip():
        grades = parse_grades_from_text(sample)
        if grades:
            return grades
        return await _extract_grades_with_ai_from_text(sample, filename)
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
