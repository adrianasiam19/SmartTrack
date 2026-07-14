#!/usr/bin/env python3
"""
generate_coremaths_lessons.py
─────────────────────────────
Reads extracted Core Mathematics SHS 1 texts from Downloads/Core Maths1/
and generates structured TypeScript lesson data for the Atlas Learning Center.

Each section produces 3–5 lessons preserving the document's pedagogical order:
  1. Introduction & Key Concepts
  2. Worked Examples
  3. Practice & Application
  4. Summary & Review
"""

import os
import re
import json
from pathlib import Path
from typing import Optional

SOURCE_DIR = r"C:\Users\Admin\Downloads\Core Maths1"
OUTPUT_FILE = Path(__file__).resolve().parent.parent / "app" / "lib" / "generatedCoreMathsLessons.ts"

SECTIONS = [
    {"id": "m1", "title": "Number Sets", "file": "LM-maths-section-1_SV.txt",
     "icon": "🔢", "color": "#4F46E5",
     "subtopics": ["Real Number System", "Properties of Operations", "Rational and Irrational Numbers", "Number Line and Ordering"]},
    {"id": "m2", "title": "Fractions and Percentages", "file": "LM-maths-section-2-LVersion.txt",
     "icon": "➗", "color": "#7C3AED",
     "subtopics": ["Types of Fractions", "Operations with Fractions", "Percentages", "Applications of Percentages"]},
    {"id": "m3", "title": "Algebraic Expressions and Factorisation", "file": "LM-maths-section-3-Tversion-1.txt",
     "icon": "✏️", "color": "#2563EB",
     "subtopics": ["Algebraic Notation", "Simplifying Expressions", "Expanding Brackets", "Factorisation"]},
    {"id": "m4", "title": "Linear Equations, Relations and Functions", "file": "LM-maths-section-4-Lversion.txt",
     "icon": "📈", "color": "#059669",
     "subtopics": ["Linear Equations", "Relations", "Functions", "Graphing"]},
    {"id": "m5", "title": "Angles and the Pythagorean Theorem", "file": "LM-maths-section-5-Lversion.txt",
     "icon": "📐", "color": "#D97706",
     "subtopics": ["Types of Angles", "Angle Relationships", "Pythagorean Theorem", "Applications"]},
    {"id": "m6", "title": "Vectors and Trigonometry", "file": "LM-maths-section-6-Lversion.txt",
     "icon": "🧭", "color": "#DC2626",
     "subtopics": ["Introduction to Vectors", "Vector Operations", "Trigonometric Ratios", "Applications"]},
    {"id": "m7", "title": "Perimeter, Area and Volume", "file": "LM-maths-section-7-Lversion.txt",
     "icon": "📏", "color": "#0891B2",
     "subtopics": ["Perimeter of Shapes", "Area of 2D Shapes", "Surface Area", "Volume of 3D Shapes"]},
    {"id": "m8", "title": "Data Organisation, Analysis and Presentation", "file": "LM-maths-section-8-Lversion.txt",
     "icon": "📊", "color": "#9333EA",
     "subtopics": ["Data Collection", "Organising Data", "Measures of Central Tendency", "Data Presentation"]},
    {"id": "m9", "title": "Probability of Independent Events", "file": "LM-maths-section-9-Lversion.txt",
     "icon": "🎲", "color": "#E11D48",
     "subtopics": ["Basic Probability", "Sample Space", "Independent Events", "Applications"]},
]


def read_text(filepath: str) -> str:
    path = os.path.join(SOURCE_DIR, filepath)
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def clean_extracted_text(text: str) -> str:
    """Clean PDF extracted text and join fragment lines into paragraphs."""
    # Remove trailing footer content
    if 'ACKNOWLEDGEMENTS' in text:
        text = text[:text.index('ACKNOWLEDGEMENTS')]
    if 'List of Contributors' in text:
        text = text[:text.index('List of Contributors')]
    
    lines = text.split('\n')
    
    # Filter out header/footer noise lines
    clean_lines = []
    for line in lines:
        s = line.strip()
        # Skip page numbers and section markers
        if s.isdigit() and len(s) <= 3:
            continue
        if s.startswith('SECTION '):
            continue
        if s == 'Year 1 Mathematics' or s == 'Year 1Mathematics':
            continue
        if not s or len(s) < 3:
            continue
        clean_lines.append(s)
    
    # Join fragment lines into paragraphs
    # Each original PDF line is a fragment - group them
    paragraphs = []
    current = []
    for line in clean_lines:
        # A new paragraph starts when the line starts with a capital letter,
        # is preceded by a blank line, or is clearly a new topic
        current.append(line)
        # If this line ends with sentence-ending punctuation and the line is substantial,
        # or if the next line looks like a header in all caps
        if line.endswith(('.', '!', '?')) and len(' '.join(current)) > 100:
            paragraphs.append(' '.join(current))
            current = []
        elif len(' '.join(current)) > 300:
            paragraphs.append(' '.join(current))
            current = []
    
    if current and len(' '.join(current)) > 40:
        paragraphs.append(' '.join(current))
    
    return paragraphs


def split_into_chunks(paragraphs: list[str], chunk_count: int = 4) -> list[list[str]]:
    """Split paragraphs into roughly equal chunks for lesson creation."""
    if len(paragraphs) <= chunk_count:
        return [[p] for p in paragraphs]
    chunk_size = max(1, len(paragraphs) // chunk_count)
    chunks = []
    for i in range(0, len(paragraphs), chunk_size):
        chunk = paragraphs[i:i + chunk_size]
        if chunk:
            chunks.append(chunk)
    # Ensure we have at most chunk_count chunks
    return chunks[:chunk_count]


def build_lesson_content(paragraphs: list[str], section: dict, lesson_idx: int, subtopic: str) -> dict:
    """Build a single lesson from paragraphs and sub-topic context."""
    lesson_id = f"coremath-{section['id']}t{lesson_idx}"
    steps = []

    # 1. Introduction / overview
    if paragraphs:
        intro = paragraphs[0]
        if len(intro) > 200:
            intro = intro[:200] + "..."
        steps.append({
            "id": f"{lesson_id}-intro",
            "type": "info",
            "content": f"**{subtopic}**\n\n{intro}"
        })

    # 2. Key concepts (info steps from content paragraphs)
    content_idx = 1
    for para in paragraphs[1:4]:  # First 3 content paragraphs
        if len(para) > 30:
            para_clean = para.strip()
            # Check if it contains example-like content
            is_example = any(kw in para_clean.upper() for kw in ["EXAMPLE", "WORKED EXAMPLE", "SOLUTION", "SOLVE"])
            if is_example:
                steps.append({
                    "id": f"{lesson_id}-example-{content_idx}",
                    "type": "info",
                    "content": f"**Worked Example {content_idx}**\n\n{para_clean}"
                })
            else:
                steps.append({
                    "id": f"{lesson_id}-content-{content_idx}",
                    "type": "info",
                    "content": para_clean
                })
            content_idx += 1

    # 3. Practice question
    practice_paras = [p for p in paragraphs[3:6] if len(p) > 40]
    if practice_paras:
        practice_text = practice_paras[0][:300]
        steps.append({
            "id": f"{lesson_id}-practice",
            "type": "question",
            "content": "Try this exercise:",
            "exercise": {
                "question": practice_text,
                "options": [
                    "I can solve this confidently",
                    "I understand the approach",
                    "I need to review the steps",
                    "I need more explanation"
                ],
                "correctIndex": 0,
                "explanation": "Self-assessment helps identify areas for improvement. Review the worked examples if needed."
            }
        })

    # 4. Additional content
    for para in paragraphs[5:8]:
        if len(para) > 50:
            steps.append({
                "id": f"{lesson_id}-content-{content_idx}",
                "type": "info",
                "content": para.strip()
            })
            content_idx += 1

    # 5. Summary / key takeaways
    summary = f"✅ **Key Takeaways: {subtopic}**\n\n" + \
              f"In this lesson, you learned about {subtopic.lower()} as part of {section['title']}. " + \
              f"Make sure you understand the core concepts before moving to the next lesson."
    steps.append({
        "id": f"{lesson_id}-summary",
        "type": "info",
        "content": summary
    })

    # 6. Checkpoint
    steps.append({
        "id": f"{lesson_id}-checkpoint",
        "type": "checkpoint",
        "content": f"Check your understanding of {subtopic}",
        "checkpoint": {
            "title": f"{subtopic} - Quick Check",
            "questions": [
                {
                    "question": f"Can you explain the main ideas of {subtopic}?",
                    "options": [
                        "Yes, I understand it well",
                        "I understand most of it",
                        "I need more practice",
                        "I need to review again"
                    ],
                    "correctIndex": 0,
                    "explanation": "Being honest about your understanding helps you focus on what needs more attention."
                },
                {
                    "question": f"How confident are you with applying {subtopic} to problems?",
                    "options": [
                        "Very confident",
                        "Fairly confident",
                        "Somewhat confident",
                        "Not yet confident"
                    ],
                    "correctIndex": 0,
                    "explanation": "Confidence grows with practice. Review the worked examples and try more exercises."
                }
            ],
            "passThreshold": 60,
            "bonusXp": 20
        }
    })

    return {
        "id": lesson_id,
        "title": subtopic,
        "subject": "Core Mathematics",
        "subjectIcon": section["icon"],
        "programme": "Both",
        "difficulty": min(5, lesson_idx),
        "estimatedMinutes": 10 + lesson_idx * 3,
        "xpReward": 25 + lesson_idx * 5,
        "unitId": "core-maths",
        "prerequisites": [],
        "shsLevels": ["SHS 1"],
        "suggestedLevel": "SHS 1",
        "steps": steps,
    }


def build_prerequisites(section_idx: int, lesson_idx: int) -> list[str]:
    """Build prerequisite chain.
    - First lesson of section 1: no prerequisites (freely accessible)
    - Subsequent lessons in same section: previous lesson in same section
    - First lesson of sections 2+: last lesson of previous section
    """
    prereqs = []
    if section_idx == 1 and lesson_idx == 1:
        # Very first lesson — no prerequisites
        return prereqs
    if lesson_idx > 1:
        # Depends on previous lesson in the same module
        prereqs.append(f"coremath-m{section_idx}t{lesson_idx - 1}")
    else:
        # First lesson of sections 2+ — depends on last lesson of previous section
        prev_section = section_idx - 1
        prev_count = len(SECTIONS[prev_section - 1]["subtopics"])
        prereqs.append(f"coremath-m{prev_section}t{prev_count}")
    return prereqs


def lesson_to_ts(lesson: dict) -> str:
    """Convert lesson dict to TypeScript source."""
    lines = []
    lines.append("  {")

    # Simple fields
    for key in ["id", "title", "subject", "subjectIcon", "programme", "unitId"]:
        val = lesson[key]
        lines.append(f'    {key}: {json.dumps(val, ensure_ascii=False)},')

    # Numeric fields
    for key in ["difficulty", "estimatedMinutes", "xpReward"]:
        lines.append(f'    {key}: {lesson[key]},')

    # Arrays
    for key in ["prerequisites", "shsLevels"]:
        lines.append(f'    {key}: {json.dumps(lesson[key], ensure_ascii=False)},')

    lines.append(f'    suggestedLevel: {json.dumps(lesson["suggestedLevel"], ensure_ascii=False)},')

    # Steps
    lines.append("    steps: [")
    for step in lesson["steps"]:
        lines.append("      {")
        lines.append(f'        id: {json.dumps(step["id"], ensure_ascii=False)},')
        lines.append(f'        type: {json.dumps(step["type"], ensure_ascii=False)},')
        lines.append(f'        content: {json.dumps(step["content"], ensure_ascii=False)},')
        if "exercise" in step:
            ex = step["exercise"]
            lines.append("        exercise: {")
            for k in ["question", "options", "correctIndex", "explanation"]:
                v = ex[k]
                if isinstance(v, str):
                    lines.append(f'          {k}: {json.dumps(v, ensure_ascii=False)},')
                else:
                    lines.append(f'          {k}: {v},')
            lines.append("        },")
        if "checkpoint" in step:
            cp = step["checkpoint"]
            lines.append("        checkpoint: {")
            lines.append(f'          title: {json.dumps(cp["title"], ensure_ascii=False)},')
            lines.append(f'          passThreshold: {cp["passThreshold"]},')
            lines.append(f'          bonusXp: {cp["bonusXp"]},')
            lines.append("          questions: [")
            for q in cp["questions"]:
                lines.append("            {")
                for k in ["question", "options", "correctIndex", "explanation"]:
                    v = q[k]
                    if isinstance(v, str):
                        lines.append(f'              {k}: {json.dumps(v, ensure_ascii=False)},')
                    else:
                        lines.append(f'              {k}: {v},')
                lines.append("            },")
            lines.append("          ],")
            lines.append("        },")
        lines.append("      },")
    lines.append("    ],")
    lines.append("  },")
    return "\n".join(lines)


def generate_header() -> str:
    return '''/**
 * generatedCoreMathsLessons.ts
 * ────────────────────────────
 * Auto-generated Core Mathematics SHS 1 lessons from
 * Ministry of Education curriculum materials.
 *
 * DO NOT EDIT DIRECTLY — re-run scripts/generate_coremaths_lessons.py instead.
 */

import type { Lesson } from './learningContent';

export const CORE_MATHS_SHS1_LESSONS: Lesson[] = [
'''


def generate_footer() -> str:
    return '''];

export const CORE_MATHS_SHS1_COUNT = '''


def main():
    print("=" * 60)
    print("  Core Mathematics SHS 1 Lesson Generator")
    print("=" * 60)

    ts_lines = [generate_header()]
    total_lessons = 0
    section_idx = 0

    for section in SECTIONS:
        section_idx += 1
        raw_text = read_text(section["file"])
        if not raw_text:
            print(f"  WARNING: No source file for {section['title']}")
            continue

        paragraphs = clean_extracted_text(raw_text)

        if not paragraphs:
            print(f"  WARNING: No paragraphs found for {section['title']}")
            continue

        # Split paragraphs into lesson chunks
        chunks = split_into_chunks(paragraphs, len(section['subtopics']))

        print(f"\n{section['title']}: {len(paragraphs)} paragraphs -> {len(chunks)} lessons")

        for idx, (chunk, subtopic) in enumerate(zip(chunks, section["subtopics"])):
            lesson_idx = idx + 1
            lesson = build_lesson_content(chunk, section, lesson_idx, subtopic)
            lesson["prerequisites"] = build_prerequisites(section_idx, lesson_idx)
            lesson["difficulty"] = lesson_idx
            lesson["estimatedMinutes"] = 8 + lesson_idx * 4
            lesson["xpReward"] = 20 + lesson_idx * 10

            ts_lines.append(lesson_to_ts(lesson))
            total_lessons += 1

            print(f"  [{lesson['id']}] {subtopic} ({len(lesson['steps'])} steps, {lesson['xpReward']} XP)")

    ts_lines.append(generate_footer())
    ts_lines.append(f"  {total_lessons};\n")

    ts_code = "\n".join(ts_lines)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(ts_code, encoding="utf-8")

    print(f"\n{'=' * 60}")
    print(f"  Generated {total_lessons} lessons total")
    print(f"  Output: {OUTPUT_FILE}")
    print(f"  File size: {len(ts_code):,} bytes")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
