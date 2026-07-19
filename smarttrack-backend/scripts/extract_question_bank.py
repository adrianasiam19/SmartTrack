"""
Extract Atlas Get-to-Know-You Question Bank from PDF → data/atlas_question_bank.json
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
PDF_PATH = ROOT / "data" / "atlas_question_bank.pdf"
OUT_PATH = ROOT / "data" / "atlas_question_bank.json"

CATEGORY_HEADERS = [
    "Learning Preferences",
    "Study Habits",
    "Problem-Solving Style",
    "Curiosity",
    "Creativity",
    "Leadership",
    "Teamwork",
    "Persistence",
    "Motivation",
    "Career Interests",
    "Decision Making",
    "Communication",
    "Time Management",
    "Confidence",
    "Academic Interests",
    "Technology Interest",
    "Engineering Interest",
    "Medical and Health Interest",
    "Environmental Interest",
    "Research Interest",
]


def extract_raw_text() -> str:
    reader = PdfReader(str(PDF_PATH))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def normalize(text: str) -> str:
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2014", "-").replace("\u2013", "-")
    text = text.replace("\ufb01", "fi").replace("\ufb02", "fl")
    text = re.sub(r"--\s*\d+\s*of\s*\d+\s*--", "\n", text)
    text = re.sub(r"End of question bank.*", "", text, flags=re.I | re.S)
    # Join hyphenated line breaks lightly
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_questions(text: str) -> list[dict]:
    header_set = set(CATEGORY_HEADERS)

    # Category positions: "1. Learning Preferences" … "20. Research Interest"
    cat_positions: list[tuple[int, str]] = []
    for i, name in enumerate(CATEGORY_HEADERS, start=1):
        m = re.search(rf"(?<!\d){i}\.\s+{re.escape(name)}(?!\s*[A-Za-z])", text)
        if not m:
            m = re.search(rf"(?<!\d){i}\.\s+{re.escape(name)}", text)
        if m:
            cat_positions.append((m.start(), name))
    cat_positions.sort(key=lambda x: x[0])

    def category_at(pos: int) -> str:
        current = CATEGORY_HEADERS[0]
        for start, name in cat_positions:
            if start <= pos:
                current = name
            else:
                break
        return current

    # Only treat N. as a question boundary when not a category header.
    # Allow missing space after period (PDF sometimes yields "100.What").
    split_pat = re.compile(r"(?<!\d)(?P<num>\d{1,3})\.\s*")
    raw_matches = list(split_pat.finditer(text))
    matches = []
    for m in raw_matches:
        num = int(m.group("num"))
        if num < 1 or num > 400:
            continue
        rest = text[m.end() : m.end() + 80]
        first = re.split(r"\s+A\.\s+", rest, maxsplit=1)[0].strip().rstrip(".")
        if first in header_set or any(rest.lstrip().startswith(h) for h in header_set):
            continue
        matches.append(m)

    questions: list[dict] = []
    seen: set[int] = set()

    for idx, m in enumerate(matches):
        num = int(m.group("num"))
        if num in seen:
            continue
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        chunk = text[start:end].strip()
        for h in header_set:
            chunk = re.sub(rf"\d+\.\s*{re.escape(h)}\s*$", "", chunk).strip()

        opt_m = re.search(
            r"^(?P<body>.+?)\s+A\.\s+(?P<a>.+?)\s+B\.\s+(?P<b>.+?)\s+C\.\s+(?P<c>.+?)\s+D\.\s+(?P<d>.+)\s*$",
            chunk,
            re.S,
        )
        if not opt_m:
            continue

        body = opt_m.group("body").strip()
        if len(body) < 12 or body.rstrip(".") in header_set:
            continue

        d_text = opt_m.group("d").strip()
        d_text = re.split(r"(?<!\d)\d{1,3}\.\s*", d_text)[0].strip().rstrip(".")

        seen.add(num)
        questions.append(
            {
                "id": f"qb-{num:03d}",
                "number": num,
                "category": category_at(m.start()),
                "text": body,
                "options": [
                    {"label": "A", "text": opt_m.group("a").strip().rstrip(".")},
                    {"label": "B", "text": opt_m.group("b").strip().rstrip(".")},
                    {"label": "C", "text": opt_m.group("c").strip().rstrip(".")},
                    {"label": "D", "text": d_text},
                ],
            }
        )

    questions.sort(key=lambda q: q["number"])
    return questions


def main() -> int:
    if not PDF_PATH.exists():
        print(f"Missing PDF: {PDF_PATH}", file=sys.stderr)
        return 1
    raw = normalize(extract_raw_text())
    questions = parse_questions(raw)
    payload = {"version": 1, "count": len(questions), "questions": questions}
    OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(questions)} questions to {OUT_PATH}")
    missing = [i for i in range(1, 401) if i not in {q["number"] for q in questions}]
    print(f"Missing count: {len(missing)}")
    if missing:
        print(f"Missing sample: {missing[:50]}")
    return 0 if len(questions) >= 350 else 1


if __name__ == "__main__":
    raise SystemExit(main())
