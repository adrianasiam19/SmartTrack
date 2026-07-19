#!/usr/bin/env python3
"""
generate_chemistry_lessons.py
─────────────────────────────
Reads extracted Chemistry SHS 1 texts from Downloads/CHEMISTRY 1/
and generates structured TypeScript lesson data for the Atlas Learning Center.
"""

import os
import json
from pathlib import Path

SOURCE_DIR = r"C:\Users\Admin\Downloads\CHEMISTRY 1"
OUTPUT_FILE = Path(__file__).resolve().parent.parent / "app" / "lib" / "generatedChemistryLessons.ts"

SECTIONS = [
    {"id": "s1", "title": "Introduction to Chemistry, Scientific Method and Atoms",
     "file": "LM-Chemistry-section-1-LVersion.txt",
     "icon": "⚗️", "color": "#0EA5E9",
     "subtopics": ["Introduction to Chemistry", "The Scientific Method in Chemistry",
                   "Atoms and Atomic Structure", "Elements, Compounds and Mixtures"]},
    {"id": "s2", "title": "The Concept of the Moles",
     "file": "LM-Chemistry-Section-2-LVersion.txt",
     "icon": "⚖️", "color": "#8B5CF6",
     "subtopics": ["The Mole Concept", "Molar Mass and Avogadro's Number",
                   "Mole Calculations", "Applications of the Mole Concept"]},
    {"id": "s3", "title": "Mole Ratios, Chemical Formulae and Chemical Equations",
     "file": "LM-Chemistry-Section-3-LVersion.txt",
     "icon": "📝", "color": "#EC4899",
     "subtopics": ["Chemical Formulae", "Balancing Chemical Equations",
                   "Mole Ratios in Reactions", "Stoichiometric Calculations"]},
    {"id": "s4", "title": "Kinetic Theory and the States of Matter (Part 1)",
     "file": "LM-Chemistry-Section-4-LVersion.txt",
     "icon": "💨", "color": "#F59E0B",
     "subtopics": ["The Kinetic Theory of Matter", "The Solid State",
                   "The Liquid State", "Changes of State"]},
    {"id": "s5", "title": "Kinetic Theory and the States of Matter (Part 2)",
     "file": "LM-Chemistry-Section-5-LVersion.txt",
     "icon": "💧", "color": "#10B981",
     "subtopics": ["The Gaseous State", "Gas Laws — Boyle's and Charles's Laws",
                   "The Ideal Gas Equation", "Diffusion and Effusion of Gases"]},
    {"id": "s6", "title": "Periodic Properties",
     "file": "LM-Chemistry-Section-6-LVersion.txt",
     "icon": "📊", "color": "#6366F1",
     "subtopics": ["The Periodic Table", "Periodic Trends — Atomic Radius",
                   "Ionisation Energy and Electronegativity", "Group and Period Properties"]},
    {"id": "s7", "title": "Inter Atomic Bonding",
     "file": "LM-Chemistry-Section-7-LVersion.txt",
     "icon": "🔗", "color": "#EF4444",
     "subtopics": ["Introduction to Chemical Bonding", "Ionic Bonding",
                   "Covalent Bonding", "Metallic Bonding"]},
    {"id": "s8", "title": "Intermolecular Bonding",
     "file": "LM-Chemistry-Section-8-LVersion.txt",
     "icon": "🧲", "color": "#14B8A6",
     "subtopics": ["Intermolecular Forces", "Hydrogen Bonding",
                   "Van der Waals Forces", "Properties Influenced by Intermolecular Forces"]},
    {"id": "s9", "title": "Qualitative and Quantitative Analysis of Organic Compounds",
     "file": "LM-Chemistry-Section-9-LVersion.txt",
     "icon": "🧪", "color": "#F97316",
     "subtopics": ["Introduction to Organic Chemistry", "Qualitative Analysis of Organic Compounds",
                   "Quantitative Analysis", "Empirical and Molecular Formulae"]},
    {"id": "s10", "title": "Classifications of Organic Compounds",
     "file": "LM-Chemistry-Section-10-LVersion.txt",
     "icon": "🧬", "color": "#06B6D4",
     "subtopics": ["Organic Functional Groups", "Hydrocarbons — Alkanes and Alkenes",
                   "Alcohols and Carboxylic Acids", "Reactions of Organic Compounds"]},
]


def read_text(filepath: str) -> str:
    path = os.path.join(SOURCE_DIR, filepath)
    if not os.path.exists(path):
        return ""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(path, "r", encoding="cp1252") as f:
            return f.read()


def clean_extracted_text(text: str) -> list[str]:
    for footer in ['ACKNOWLEDGEMENTS', 'List of Contributors', 'REFERENCES']:
        if footer in text:
            text = text[:text.index(footer)]

    lines = text.split('\n')
    clean_lines = []
    for line in lines:
        s = line.strip()
        if s.isdigit() and len(s) <= 3:
            continue
        if s.startswith('SECTION ') or s.startswith('Section '):
            continue
        if 'Chemistry Year 1' in s:
            continue
        if not s or len(s) < 3:
            continue
        clean_lines.append(s)

    paragraphs = []
    current = []
    for line in clean_lines:
        current.append(line)
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
    if len(paragraphs) <= chunk_count:
        return [[p] for p in paragraphs]
    chunk_size = max(1, len(paragraphs) // chunk_count)
    chunks = []
    for i in range(0, len(paragraphs), chunk_size):
        chunk = paragraphs[i:i + chunk_size]
        if chunk:
            chunks.append(chunk)
    return chunks[:chunk_count]


def build_lesson_content(paragraphs: list[str], section: dict, lesson_idx: int, subtopic: str) -> dict:
    lesson_id = f"chem-{section['id']}t{lesson_idx}"
    steps = []

    if paragraphs:
        intro = paragraphs[0]
        if len(intro) > 200:
            intro = intro[:200] + "..."
        steps.append({
            "id": f"{lesson_id}-intro",
            "type": "info",
            "content": f"**{subtopic}**\n\n{intro}"
        })

    content_idx = 1
    for para in paragraphs[1:4]:
        if len(para) > 30:
            para_clean = para.strip()
            is_activity = any(kw in para_clean.upper() for kw in ["ACTIVITY", "EXERCISE", "TASK", "LEARNING TASK"])
            if is_activity:
                steps.append({
                    "id": f"{lesson_id}-activity-{content_idx}",
                    "type": "info",
                    "content": f"**Activity {content_idx}**\n\n{para_clean[:500]}"
                })
            else:
                steps.append({
                    "id": f"{lesson_id}-content-{content_idx}",
                    "type": "info",
                    "content": para_clean
                })
            content_idx += 1

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
                    "I understand this well",
                    "I understand most of it",
                    "I need to review the concepts",
                    "I need more explanation"
                ],
                "correctIndex": 0,
                "explanation": "Self-assessment helps identify areas for improvement. Review the concepts and activities if needed."
            }
        })

    for para in paragraphs[5:8]:
        if len(para) > 50:
            steps.append({
                "id": f"{lesson_id}-content-{content_idx}",
                "type": "info",
                "content": para.strip()
            })
            content_idx += 1

    summary = f"✅ **Key Takeaways: {subtopic}**\n\n" + \
              f"In this lesson, you learned about {subtopic.lower()} as part of {section['title']}. " + \
              f"Make sure you understand the core concepts before moving to the next lesson."
    steps.append({
        "id": f"{lesson_id}-summary",
        "type": "info",
        "content": summary
    })

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
                    "question": f"How confident are you with applying {subtopic} to real-life situations?",
                    "options": [
                        "Very confident",
                        "Fairly confident",
                        "Somewhat confident",
                        "Not yet confident"
                    ],
                    "correctIndex": 0,
                    "explanation": "Confidence grows with practice. Review the activities and try more exercises."
                }
            ],
            "passThreshold": 60,
            "bonusXp": 20
        }
    })

    return {
        "id": lesson_id,
        "title": subtopic,
        "subject": "Chemistry",
        "subjectIcon": section["icon"],
        "programme": "Both",
        "difficulty": min(5, lesson_idx),
        "estimatedMinutes": 10 + lesson_idx * 3,
        "xpReward": 25 + lesson_idx * 5,
        "unitId": "chemistry",
        "prerequisites": [],
        "shsLevels": ["SHS 1"],
        "suggestedLevel": "SHS 1",
        "steps": steps,
    }


def build_prerequisites(section_idx: int, lesson_idx: int) -> list[str]:
    prereqs = []
    if section_idx == 1 and lesson_idx == 1:
        return prereqs
    if lesson_idx > 1:
        sr = SECTIONS[section_idx - 1]
        prereqs.append(f"chem-{sr['id']}t{lesson_idx - 1}")
    else:
        prev = SECTIONS[section_idx - 2]
        prev_count = len(prev["subtopics"])
        prereqs.append(f"chem-{prev['id']}t{prev_count}")
    return prereqs


def lesson_to_ts(lesson: dict) -> str:
    lines = []
    lines.append("  {")
    for key in ["id", "title", "subject", "subjectIcon", "programme", "unitId"]:
        val = lesson[key]
        lines.append(f'    {key}: {json.dumps(val, ensure_ascii=False)},')
    for key in ["difficulty", "estimatedMinutes", "xpReward"]:
        lines.append(f'    {key}: {lesson[key]},')
    for key in ["prerequisites", "shsLevels"]:
        lines.append(f'    {key}: {json.dumps(lesson[key], ensure_ascii=False)},')
    lines.append(f'    suggestedLevel: {json.dumps(lesson["suggestedLevel"], ensure_ascii=False)},')
    lines.append("    steps: [")
    for step in lesson["steps"]:
        lines.append("      {")
        lines.append(f'        id: {json.dumps(step["id"], ensure_ascii=False)},')
        lines.append(f'        type: {json.dumps(step["type"], ensure_ascii=False)},')
        s = step["content"]
        if '`' in s:
            s = s.replace('`', '\\`')
        lines.append(f'        content: {json.dumps(s, ensure_ascii=False)},')
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
 * generatedChemistryLessons.ts
 * ────────────────────────────
 * Auto-generated Chemistry SHS 1 lessons from
 * Ministry of Education curriculum materials.
 *
 * DO NOT EDIT DIRECTLY — re-run scripts/generate_chemistry_lessons.py instead.
 */

import type { Lesson } from './learningContent';

export const CHEMISTRY_SHS1_LESSONS: Lesson[] = [
'''


def generate_footer() -> str:
    return '''];

export const CHEMISTRY_SHS1_COUNT = '''


def main():
    print("=" * 60)
    print("  Chemistry SHS 1 Lesson Generator")
    print("=" * 60)

    ts_lines = [generate_header()]
    total_lessons = 0

    for section_idx, section in enumerate(SECTIONS, 1):
        raw_text = read_text(section["file"])
        if not raw_text:
            print(f"  WARNING: No source file for {section['title']}")
            continue

        paragraphs = clean_extracted_text(raw_text)
        if not paragraphs:
            print(f"  WARNING: No paragraphs found for {section['title']}")
            continue

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
