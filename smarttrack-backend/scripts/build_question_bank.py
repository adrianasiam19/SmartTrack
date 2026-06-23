"""
build_question_bank.py
───────────────────────
Master question bank generator for the Atlas Challenge Arena.

Generates ~800 questions across 4 arenas:
  - Logic Arena          (200+ questions)
  - Quantitative Sprint  (200+ questions)
  - Scientific Thinking  (200+ questions)
  - Communication        (200+ questions)

Each question is parameterised from templates for anti-cheating support.
Output: smarttrack-backend/data/questions_v2.json

Usage:
  python -m scripts.build_question_bank

The generated JSON can be loaded by seed_questions.py to populate the database.
"""

import json
from pathlib import Path
import sys

# Add parent to path so we can import app modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.assessment.question_templates import build_all_templates, generate_bank


def main():
    """Generate the complete question bank and write to questions_v2.json."""
    print("=" * 60)
    print("  ATLAS CHALLENGE ARENA — Question Bank Generator")
    print("=" * 60)

    # Build all templates from the core module
    all_templates = build_all_templates()

    print(f"\n  Total templates:      {len(all_templates)}")

    # Count per arena
    arena_counts = {}
    for t in all_templates:
        arena_counts[t.arena] = arena_counts.get(t.arena, 0) + 1
    for arena, count in sorted(arena_counts.items()):
        print(f"    • {arena}: {count} templates")

    # Generate question variants
    # 15 variants per template → ~855 questions (57 × 15)
    bank = generate_bank(all_templates, questions_per_template=15, seed=42)
    print(f"\n  Total questions generated: {len(bank)}")

    # Count per arena and tier
    arena_q_counts = {}
    tier_counts = {}
    for q in bank:
        arena_q_counts[q["arena"]] = arena_q_counts.get(q["arena"], 0) + 1
        tier_counts[q["difficulty_tier"]] = tier_counts.get(q["difficulty_tier"], 0) + 1

    print(f"\n  Questions by Arena:")
    for arena, count in sorted(arena_q_counts.items()):
        print(f"    • {arena.upper():20s}  {count:4d}")

    print(f"\n  Questions by Difficulty Tier:")
    for tier, count in sorted(tier_counts.items()):
        print(f"    • {tier:10s}  {count:4d}")

    # Write to file
    data_dir = Path(__file__).resolve().parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    output_path = data_dir / "questions_v2.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(bank, f, indent=2, ensure_ascii=False)

    print(f"\n  ✅ Written to: {output_path}")
    print(f"  File size: {output_path.stat().st_size / 1024:.1f} KB")
    print(f"\n  {'=' * 60}")


if __name__ == "__main__":
    main()
