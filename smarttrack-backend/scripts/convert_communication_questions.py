"""
convert_communication_questions.py
────────────────────────────────────
Converts the Communication Arena (SHS 1) question bank JSON
into the DB-ready format matching questions_v2.json.
"""

import json
import sys
from pathlib import Path

# Windows console encoding fix
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_source() -> dict:
    """Load the pasted question bank JSON."""
    path = DATA_DIR / "communication_raw.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    raise FileNotFoundError(
        "Please save the pasted JSON to smarttrack-backend/data/communication_raw.json"
    )


def xp_to_difficulty_b(xp: int) -> float:
    """
    Map XP value to an IRT difficulty_b parameter in the Bronze range (-1.5 to -0.5).
    XP range: 10-30  →  b range: -1.5 (easy) to -0.5 (harder)
    """
    return round(-1.5 + (xp - 10) * (1.0 / 20), 2)


def find_answer_letter(options: list, answer_text: str) -> str:
    """Find which letter (A/B/C/D) corresponds to the answer text."""
    letters = ["A", "B", "C", "D"]
    for i, opt in enumerate(options):
        if opt.strip() == answer_text.strip():
            return letters[i]
    return "A"


def convert_question(q: dict, idx: int) -> dict:
    """Convert a single question from the source format to DB format."""
    options_list = q["options"]
    options_dict = {
        "A": options_list[0],
        "B": options_list[1],
        "C": options_list[2],
        "D": options_list[3],
    }
    correct_letter = find_answer_letter(options_list, q["answer"])
    xp = q.get("xp", 20)

    return {
        "id": idx,
        "arena": "communication",
        "domain": "Verbal",
        "category": q["category"],
        "mission_title": q.get("mission_title", ""),
        "difficulty_tier": "Bronze",
        "shs_levels": ["SHS 1"],
        "difficulty_a": 1.0,
        "difficulty_b": xp_to_difficulty_b(xp),
        "difficulty_c": 0.25,
        "question": q["question"],
        "options": options_dict,
        "correct_answer": correct_letter,
        "explanation": q["explanation"],
        "template_id": None,
        "source_id": q["id"],
    }


def main():
    source = load_source()
    questions = source.get("questions", [])
    print(f"Loaded {len(questions)} questions from source.")

    converted = []
    for idx, q in enumerate(questions, start=1):
        converted.append(convert_question(q, idx))

    output_path = DATA_DIR / "communication_shs1.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(converted, f, indent=2, ensure_ascii=False)

    print(f"OK Converted {len(converted)} questions.")
    print(f"Saved to: {output_path}")

    # Print summary
    categories = {}
    for q in converted:
        cat = q["category"]
        categories[cat] = categories.get(cat, 0) + 1
    print(f"\nBreakdown by category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count} questions")


if __name__ == "__main__":
    main()
