"""
Expand data/phase_academic_bank.json with original MCQs via DeepSeek.

Uses curriculum lesson titles as topic seeds. Does NOT scrape WAEC past papers.

Usage (from smarttrack-backend, with DEEPSEEK_API_KEY set):
    python -m scripts.expand_phase_academic_bank --count 20
    python -m scripts.expand_phase_academic_bank --count 8 --shs "SHS 2" --subject core_maths
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.config import settings  # noqa: E402

BANK_PATH = ROOT / "data" / "phase_academic_bank.json"
CURRICULUM_PATH = ROOT / "data" / "curriculum_lessons.json"

SUBJECT_KEYS = ("english", "core_maths", "integrated_science", "social_studies")
SHS_LEVELS = ("SHS 1", "SHS 2", "SHS 3")

SUBJECT_ALIASES = {
    "english": ("english", "eng lang", "language"),
    "core_maths": ("math", "mathematics", "core maths"),
    "integrated_science": ("science", "integrated science", "biology", "chemistry", "physics"),
    "social_studies": ("social", "social studies", "civic"),
}


def _load_bank() -> list[dict]:
    if not BANK_PATH.exists():
        return []
    return json.loads(BANK_PATH.read_text(encoding="utf-8"))


def _topic_seeds(subject: str, shs_level: str, limit: int = 8) -> list[str]:
    if not CURRICULUM_PATH.exists():
        return [f"{subject} fundamentals", f"{subject} problem solving"]
    raw = json.loads(CURRICULUM_PATH.read_text(encoding="utf-8"))
    lessons = raw if isinstance(raw, list) else raw.get("lessons", [])
    aliases = SUBJECT_ALIASES.get(subject, (subject,))
    seeds: list[str] = []
    for lesson in lessons:
        levels = lesson.get("shs_levels") or lesson.get("shsLevels") or []
        if shs_level not in levels and levels:
            continue
        subj = str(lesson.get("subject") or lesson.get("unit") or "").lower()
        title = str(lesson.get("title") or lesson.get("name") or "").strip()
        if not title:
            continue
        if any(a in subj for a in aliases) or any(a in title.lower() for a in aliases):
            seeds.append(title)
        if len(seeds) >= limit:
            break
    return seeds or [f"{subject} {shs_level} core concepts"]


def _parse_json(content: str) -> dict | list | None:
    content = content.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        m = re.search(r"(\{.*\}|\[.*\])", content, re.S)
        if m:
            try:
                return json.loads(m.group(1))
            except json.JSONDecodeError:
                return None
    return None


async def _generate_batch(
    *,
    subject: str,
    shs_level: str,
    exam_style: str,
    count: int,
    topics: list[str],
    existing_ids: set[str],
) -> list[dict]:
    if not settings.DEEPSEEK_API_KEY:
        raise SystemExit("DEEPSEEK_API_KEY is not set")

    style_note = (
        "Write WASSCE-style application items (original — do not copy past papers)."
        if exam_style == "wassce"
        else "Write classroom formative MCQs appropriate for this year group."
    )
    prompt = (
        f"Create {count} ORIGINAL Ghana secondary school MCQs for subject key '{subject}'.\n"
        f"Target level: {shs_level}. Style: {exam_style}. {style_note}\n"
        f"Topic seeds (use as inspiration, not as titles): {', '.join(topics[:6])}\n"
        "Each item must be unique and curriculum-aligned.\n"
        "Return ONLY a JSON array of objects with keys:\n"
        "id (string slug), subject, shs_level, exam_style, difficulty (1-15 int),\n"
        "question_text, options (object A-D), correct_answer (A-D), explanation.\n"
        f"Use subject exactly '{subject}', shs_level exactly '{shs_level}', "
        f"exam_style exactly '{exam_style}'."
    )

    async with httpx.AsyncClient(timeout=90.0) as client:
        res = await client.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}"},
            json={
                "model": settings.DEEPSEEK_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You write original educational MCQs for Ghana SHS/WASSCE-style "
                            "practice. Never reproduce copyrighted past papers. JSON only."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.8,
            },
        )
        res.raise_for_status()
        content = res.json()["choices"][0]["message"]["content"]

    parsed = _parse_json(content)
    if isinstance(parsed, dict) and "questions" in parsed:
        parsed = parsed["questions"]
    if not isinstance(parsed, list):
        raise RuntimeError("Model did not return a JSON array")

    cleaned: list[dict] = []
    for i, item in enumerate(parsed):
        if not isinstance(item, dict):
            continue
        qtext = item.get("question_text")
        ans = item.get("correct_answer")
        opts = item.get("options") or {}
        if not qtext or not ans:
            continue
        if isinstance(opts, list):
            opts = {chr(65 + j): str(o) for j, o in enumerate(opts[:4])}
        qid = str(item.get("id") or f"gen-{subject}-{shs_level}-{exam_style}-{i}").replace(" ", "-")
        if qid in existing_ids:
            qid = f"{qid}-{len(existing_ids)+i}"
        existing_ids.add(qid)
        cleaned.append(
            {
                "id": qid,
                "subject": subject,
                "shs_level": shs_level,
                "exam_style": exam_style,
                "difficulty": int(item.get("difficulty") or (12 if exam_style == "wassce" else 5)),
                "question_text": qtext,
                "options": opts,
                "correct_answer": str(ans).strip().upper()[:1],
                "explanation": item.get("explanation") or "",
            }
        )
    return cleaned


async def main() -> None:
    parser = argparse.ArgumentParser(description="Expand phase academic question bank")
    parser.add_argument("--count", type=int, default=12, help="Questions to generate this run")
    parser.add_argument("--subject", choices=SUBJECT_KEYS, default=None)
    parser.add_argument("--shs", choices=SHS_LEVELS, default=None)
    parser.add_argument(
        "--wassce",
        action="store_true",
        help="Tag new items as exam_style=wassce (Phase 3 pool)",
    )
    args = parser.parse_args()

    bank = _load_bank()
    existing_ids = {str(q.get("id")) for q in bank if q.get("id")}
    subject = args.subject or "core_maths"
    shs = args.shs or ("SHS 3" if args.wassce else "SHS 1")
    style = "wassce" if args.wassce else "classroom"
    topics = _topic_seeds(subject, shs)

    print(f"Generating {args.count} {style} items for {subject} / {shs} ...")
    new_items = await _generate_batch(
        subject=subject,
        shs_level=shs,
        exam_style=style,
        count=args.count,
        topics=topics,
        existing_ids=existing_ids,
    )
    if not new_items:
        raise SystemExit("No valid questions returned")

    bank.extend(new_items)
    BANK_PATH.write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Appended {len(new_items)} questions. Bank total: {len(bank)}")


if __name__ == "__main__":
    asyncio.run(main())
