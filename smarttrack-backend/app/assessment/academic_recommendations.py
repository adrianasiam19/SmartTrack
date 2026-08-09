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
from difflib import SequenceMatcher
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

# Minimum subject grades before we offer confirmation.
MIN_GRADES_FOR_CONFIRM = 4
# Fuzzy / token overlap threshold for profile vs slip name.
MIN_NAME_MATCH_SCORE = 0.72

_NAME_TITLES = {
    "mr",
    "mrs",
    "miss",
    "ms",
    "master",
    "dr",
    "prof",
    "sir",
    "madam",
}

_CANDIDATE_NAME_PATTERNS = [
    re.compile(
        r"candidate'?s?\s+name\s*[:\-.]?\s*(?P<name>[A-Za-z][A-Za-z .'-]{1,80})",
        re.I,
    ),
    re.compile(
        r"name\s+of\s+candidate\s*[:\-.]?\s*(?P<name>[A-Za-z][A-Za-z .'-]{1,80})",
        re.I,
    ),
    re.compile(
        r"student\s*name\s*[:\-.]?\s*(?P<name>[A-Za-z][A-Za-z .'-]{1,80})",
        re.I,
    ),
    re.compile(
        r"candidate'?s?\s+name\s*[:\-.]?\s*\n\s*(?P<name>[A-Za-z][A-Za-z .'-]{1,80})",
        re.I,
    ),
]

# Strong exam-board cues (any one is enough with grades).
_WAEC_STRONG_PATTERNS = [
    re.compile(r"west\s+african\s+examinations?\s+council", re.I),
    re.compile(r"\bwaec\b", re.I),
    re.compile(r"\bwassce\b", re.I),
    re.compile(r"west\s+african\s+senior\s+school\s+certificate", re.I),
    re.compile(r"senior\s+school\s+certificate\s+examination", re.I),
    re.compile(r"statement\s+of\s+results", re.I),
]

# Supporting layout cues on official slips.
_WAEC_CONTEXT_PATTERNS = [
    re.compile(r"candidate\s*(?:name|no\.?|number|index)", re.I),
    re.compile(r"centre\s*(?:name|no\.?|number)", re.I),
    re.compile(r"index\s*(?:no\.?|number)", re.I),
    re.compile(r"examination\s+year", re.I),
    re.compile(r"school\s+code", re.I),
]

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


def assess_waec_document(
    text: str,
    *,
    grades: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """
    Heuristic gate: does this look like a WAEC/WASSCE results document?

    Not cryptographic authentication — rejects common non-results PDFs that
    merely mention a subject name.
    """
    sample = (text or "").strip()
    grade_count = len(grades or [])
    reasons: list[str] = []

    if not sample and grade_count == 0:
        return {
            "is_waec": False,
            "confidence": 0.0,
            "reasons": ["no_readable_text"],
        }

    strong_hits = [p.pattern for p in _WAEC_STRONG_PATTERNS if p.search(sample)]
    context_hits = [p.pattern for p in _WAEC_CONTEXT_PATTERNS if p.search(sample)]

    if strong_hits:
        reasons.append("waec_marker")
    if context_hits:
        reasons.append("results_layout_marker")
    if grade_count >= MIN_GRADES_FOR_CONFIRM:
        reasons.append("enough_subject_grades")

    # Strong board marker + any grades, or layout cues + enough grades.
    if strong_hits and grade_count >= 1:
        confidence = 0.9 if grade_count >= MIN_GRADES_FOR_CONFIRM else 0.7
        return {"is_waec": True, "confidence": confidence, "reasons": reasons}
    if strong_hits and grade_count == 0:
        # Marker present but no grades yet — still treat as WAEC-looking for AI retry.
        return {"is_waec": True, "confidence": 0.55, "reasons": reasons + ["marker_only"]}
    if context_hits and grade_count >= MIN_GRADES_FOR_CONFIRM:
        return {"is_waec": True, "confidence": 0.75, "reasons": reasons}

    return {
        "is_waec": False,
        "confidence": 0.2 if grade_count else 0.05,
        "reasons": reasons or ["no_waec_markers"],
    }


def _clean_person_name(raw: str | None) -> str:
    if not raw:
        return ""
    cleaned = re.sub(r"[^A-Za-z\s\-']", " ", str(raw))
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" -'")
    return cleaned


def name_tokens(raw: str | None) -> list[str]:
    cleaned = _clean_person_name(raw).lower()
    if not cleaned:
        return []
    tokens: list[str] = []
    for part in cleaned.replace("-", " ").split():
        tok = part.strip("'")
        if len(tok) < 2:
            continue
        if tok in _NAME_TITLES:
            continue
        tokens.append(tok)
    return tokens


def extract_candidate_name_from_text(text: str) -> str | None:
    """Pull the candidate name from WASSCE-style PDF/plain text."""
    if not text or not text.strip():
        return None
    for pat in _CANDIDATE_NAME_PATTERNS:
        m = pat.search(text)
        if not m:
            continue
        name = _clean_person_name(m.group("name"))
        # Avoid labels / junk
        low = name.lower()
        if not name or len(name) < 3:
            continue
        if any(
            bad in low
            for bad in ("candidate", "centre", "center", "school", "examination", "waec")
        ):
            continue
        if len(name_tokens(name)) >= 1:
            return name
    return None


def compare_candidate_to_profile(
    profile_name: str | None,
    document_name: str | None,
) -> dict[str, Any]:
    """
    Cross-check profile full_name against the name printed on the results slip.

    Tolerates surname/first-name order and missing middle names, but rejects
    clearly different people.
    """
    profile = _clean_person_name(profile_name)
    document = _clean_person_name(document_name)
    p_tokens = name_tokens(profile)
    d_tokens = name_tokens(document)

    if len(p_tokens) < 2:
        return {
            "matched": False,
            "score": 0.0,
            "reason": "profile_name_incomplete",
            "profile_name": profile,
            "document_name": document,
        }
    if not d_tokens:
        return {
            "matched": False,
            "score": 0.0,
            "reason": "document_name_missing",
            "profile_name": profile,
            "document_name": document,
        }

    p_set = set(p_tokens)
    d_set = set(d_tokens)
    shared = p_set & d_set
    # Coverage of the shorter name (order-independent).
    shorter = p_set if len(p_set) <= len(d_set) else d_set
    longer = d_set if shorter is p_set else p_set
    containment = len(shared) / max(len(shorter), 1)

    # Sorted-token string similarity (handles minor spelling drift).
    seq = SequenceMatcher(
        None,
        " ".join(sorted(p_tokens)),
        " ".join(sorted(d_tokens)),
    ).ratio()

    score = max(containment, seq)

    # Exact or full containment of one name in the other.
    if p_set == d_set or shorter <= longer:
        return {
            "matched": True,
            "score": max(score, 0.95),
            "reason": "name_match",
            "profile_name": profile,
            "document_name": document,
        }

    # At least two shared tokens, or one shared if both are single-token (rare).
    need = 2 if min(len(p_set), len(d_set)) >= 2 else 1
    if len(shared) >= need and score >= MIN_NAME_MATCH_SCORE:
        return {
            "matched": True,
            "score": score,
            "reason": "name_match",
            "profile_name": profile,
            "document_name": document,
        }

    # Strong fuzzy only when both sides share the longest token (often surname).
    longest_p = max(p_tokens, key=len)
    if longest_p in d_set and score >= 0.85 and len(shared) >= 1:
        return {
            "matched": True,
            "score": score,
            "reason": "name_match_fuzzy",
            "profile_name": profile,
            "document_name": document,
        }

    return {
        "matched": False,
        "score": score,
        "reason": "name_mismatch",
        "profile_name": profile,
        "document_name": document,
    }


async def _extract_grades_with_ai_from_text(
    text: str, filename: str
) -> dict[str, Any]:
    prompt = (
        "You extract grades ONLY from WAEC/WASSCE (West African Examinations Council) "
        "results text.\n"
        "Return ONLY valid JSON:\n"
        '{"is_waec_results":true,"exam_type":"WASSCE","candidate_name":"JOHN DOE KWAME",'
        '"grades":[{"subject":"Core Mathematics","grade":"B3"}]}\n'
        "Always include candidate_name exactly as printed when present.\n"
        "If the text is not clearly a WAEC/WASSCE results document, return "
        '{"is_waec_results":false,"exam_type":null,"candidate_name":null,"grades":[]}.\n'
        "Do not invent subjects, grades, or names."
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
            return {"grades": [], "candidate_name": None}
        if parsed.get("is_waec_results") is False:
            return {"grades": [], "candidate_name": None}
        return {
            "grades": _normalize_grade_records(
                parsed.get("grades") or parsed.get("results") or []
            ),
            "candidate_name": _clean_person_name(parsed.get("candidate_name")) or None,
        }
    except Exception as e:
        logger.warning("AI grade extraction from text failed: %s", e)
        return {"grades": [], "candidate_name": None}


async def _analyze_image_document(
    *,
    filename: str,
    content_type: str | None,
    data: bytes,
) -> dict[str, Any]:
    prompt = (
        "You verify whether this image is a WAEC/WASSCE results document "
        "(results slip, statement of results, or clear photocopy of one), "
        "then extract the candidate name and subject grades if it is.\n"
        "Return ONLY valid JSON:\n"
        '{"is_waec_results":true,"confidence":0.0,"document_kind":"wassce_results",'
        '"candidate_name":"JOHN DOE KWAME",'
        '"grades":[{"subject":"Core Mathematics","grade":"B3"}]}\n'
        "candidate_name must be copied exactly from the slip when visible.\n"
        "If it is NOT clearly WAEC/WASSCE results (e.g. school report, transcript, "
        "ID card, random homework, screenshot of something else), set "
        'is_waec_results to false, grades to [], candidate_name to null, '
        "and document_kind to a short label.\n"
        "Do not invent grades or names."
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
            return {
                "grades": [],
                "candidate_name": None,
                "waec": {
                    "is_waec": False,
                    "confidence": 0.0,
                    "reasons": ["ai_parse_failed"],
                },
            }
        is_waec = bool(parsed.get("is_waec_results"))
        grades = (
            _normalize_grade_records(parsed.get("grades") or parsed.get("results") or [])
            if is_waec
            else []
        )
        try:
            confidence = float(parsed.get("confidence") or (0.8 if is_waec else 0.2))
        except (TypeError, ValueError):
            confidence = 0.8 if is_waec else 0.2
        kind = str(parsed.get("document_kind") or ("wassce_results" if is_waec else "other"))
        return {
            "grades": grades,
            "candidate_name": (
                _clean_person_name(parsed.get("candidate_name")) or None
                if is_waec
                else None
            ),
            "waec": {
                "is_waec": is_waec,
                "confidence": max(0.0, min(1.0, confidence)),
                "reasons": ["vision_model", kind],
            },
        }
    except Exception as e:
        logger.warning("Image grade extraction failed: %s", e)
        return {
            "grades": [],
            "candidate_name": None,
            "waec": {
                "is_waec": False,
                "confidence": 0.0,
                "reasons": ["vision_error"],
            },
        }


async def extract_grades_with_ai(
    *,
    filename: str,
    content_type: str | None,
    data: bytes,
) -> list[dict[str, str]]:
    """Backward-compatible wrapper — prefer analyze_academic_document."""
    result = await analyze_academic_document(
        filename=filename,
        content_type=content_type,
        data=data,
    )
    return list(result.get("grades") or [])


async def analyze_academic_document(
    *,
    filename: str,
    content_type: str | None,
    data: bytes,
    profile_name: str | None = None,
) -> dict[str, Any]:
    """
    Extract grades and decide whether the file looks like WAEC/WASSCE results.

    Returns:
      grades, waec, candidate_name, name_match, method
    """
    ext = Path(filename).suffix.lower()
    is_pdf = ext == ".pdf" or (content_type or "").lower() == "application/pdf"
    is_image = (content_type or "").startswith("image/") or ext in {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
    }

    async def _from_text(text: str, method: str) -> dict[str, Any]:
        grades = parse_grades_from_text(text)
        candidate_name = extract_candidate_name_from_text(text)
        waec = assess_waec_document(text, grades=grades)
        # Only ask the LLM when the document already looks like WAEC,
        # or when markers are present but regex missed the table / name.
        if (not grades or not candidate_name) and (
            waec["is_waec"] or waec["confidence"] >= 0.55
        ):
            ai = await _extract_grades_with_ai_from_text(text, filename)
            if not grades:
                grades = list(ai.get("grades") or [])
            if not candidate_name:
                candidate_name = ai.get("candidate_name")
            waec = assess_waec_document(text, grades=grades)
        elif grades and not waec["is_waec"]:
            waec = assess_waec_document(text, grades=grades)
        name_match = compare_candidate_to_profile(profile_name, candidate_name)
        return {
            "grades": grades,
            "waec": waec,
            "candidate_name": candidate_name,
            "name_match": name_match,
            "method": method,
        }

    if is_pdf:
        pdf_text = extract_text_from_pdf(data)
        if not pdf_text:
            logger.warning(
                "pypdf extracted no text from %s (may be a scanned/image-only PDF)",
                filename,
            )
            return {
                "grades": [],
                "candidate_name": None,
                "name_match": compare_candidate_to_profile(profile_name, None),
                "waec": {
                    "is_waec": False,
                    "confidence": 0.0,
                    "reasons": ["no_readable_text"],
                },
                "method": "pdf_empty",
            }
        return await _from_text(pdf_text, "pdf_text")

    if is_image:
        vision = await _analyze_image_document(
            filename=filename,
            content_type=content_type,
            data=data,
        )
        candidate_name = vision.get("candidate_name")
        return {
            "grades": vision["grades"],
            "waec": vision["waec"],
            "candidate_name": candidate_name,
            "name_match": compare_candidate_to_profile(profile_name, candidate_name),
            "method": "image_vision",
        }

    pdf_text = extract_text_from_pdf(data)
    if pdf_text:
        return await _from_text(pdf_text, "binary_pdf")

    sample = data[:12000].decode("utf-8", errors="ignore")
    if sample.strip():
        return await _from_text(sample, "plain_text")

    return {
        "grades": [],
        "candidate_name": None,
        "name_match": compare_candidate_to_profile(profile_name, None),
        "waec": {
            "is_waec": False,
            "confidence": 0.0,
            "reasons": ["unreadable"],
        },
        "method": "none",
    }


def merge_academic_upload_into_profile(
    existing_profile: dict | None,
    *,
    filename: str,
    stored_name: str,
    grades: list[dict[str, str]],
    confirmed: bool = True,
) -> dict:
    profile = dict(existing_profile or {})
    profile["academic_upload"] = {
        "filename": filename,
        "stored_name": stored_name,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "grades": grades,
        "grades_extracted": bool(grades),
        "confirmed": confirmed,
    }
    profile.pop("academic_upload_pending", None)
    return profile


def merge_academic_pending_into_profile(
    existing_profile: dict | None,
    *,
    filename: str,
    stored_name: str,
    grades: list[dict[str, str]],
    waec: dict[str, Any] | None = None,
    candidate_name: str | None = None,
    name_match: dict[str, Any] | None = None,
) -> dict:
    """Store extraction preview until the learner confirms."""
    profile = dict(existing_profile or {})
    profile["academic_upload_pending"] = {
        "filename": filename,
        "stored_name": stored_name,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "grades": grades,
        "waec": waec or {},
        "candidate_name": candidate_name,
        "name_match": name_match or {},
    }
    return profile


def clear_academic_pending_from_profile(existing_profile: dict | None) -> dict:
    profile = dict(existing_profile or {})
    profile.pop("academic_upload_pending", None)
    return profile


def clear_academic_upload_from_profile(existing_profile: dict | None) -> dict:
    profile = dict(existing_profile or {})
    profile.pop("academic_upload", None)
    profile.pop("academic_upload_pending", None)
    profile.pop("wassce_uploaded", None)
    profile.pop("academic_results_uploaded", None)
    return profile


def delete_stored_academic_file(user_id: str, stored_name: str | None) -> None:
    if not stored_name or stored_name == "manual_entry":
        return
    safe = Path(stored_name).name
    path = UPLOAD_ROOT / str(user_id) / safe
    try:
        if path.is_file():
            path.unlink()
    except OSError as e:
        logger.warning("Could not delete academic file %s: %s", path, e)


def has_academic_upload(user) -> bool:
    profile = getattr(user, "learner_profile", None) or {}
    upload = profile.get("academic_upload") if isinstance(profile, dict) else None
    if not upload or not upload.get("filename"):
        return False
    # Pending-only uploads do not count; confirmed flag defaults true for legacy rows.
    if upload.get("confirmed") is False:
        return False
    return bool(upload.get("grades_extracted") or upload.get("grades"))


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
