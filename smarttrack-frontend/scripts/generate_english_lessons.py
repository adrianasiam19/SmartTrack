#!/usr/bin/env python3
"""
generate_english_lessons.py
───────────────────────────
Reads extracted English Language SHS 1 texts from Downloads/
and generates structured TypeScript lesson data for the Atlas Learning Center.

Each section produces 4 lessons preserving the document's pedagogical order:
  1. Introduction & Key Concepts
  2. Deeper Dive / Activities
  3. Practical Application
  4. Summary & Review
"""

import os
import re
import json
from pathlib import Path
from typing import Optional

SOURCE_DIR = r"C:\Users\Admin\Downloads"
OUTPUT_FILE = Path(__file__).resolve().parent.parent / "app" / "lib" / "generatedEnglishLessons.ts"

SECTIONS = [
    {"id": "s5", "title": "Discourse and Conversation, Summarising Text and Forms of Adjectives",
     "file": "English-Language_LM_Year-1_Section-5-LV.txt",
     "icon": "💬", "color": "#D97706",
     "subtopics": ["Conversation and Communication in Context", "Formal and Informal Language",
                   "Parts and Elements of a Story", "Forms of Adjectives"]},
    {"id": "s7", "title": "Oral Language, Reading and Grammar",
     "file": "English-Language_LM_Year-1_Section-7-LV.txt",
     "icon": "🔊", "color": "#7C3AED",
     "subtopics": ["Consonant Sounds — Plosives and Fricatives", "Retrieving and Interpreting Information",
                   "Reading Comprehension Strategies", "Language Use in Different Contexts"]},
    {"id": "s8", "title": "Forms of Verbs, Writing Paragraph Strategies and Creating Monologues and Dialogues",
     "file": "English-Language_LM_Year-1_Section-8-LV.txt",
     "icon": "📝", "color": "#0284C7",
     "subtopics": ["Introduction to Verbs — Tense and Aspect", "Forms of Verbs and Auxiliaries",
                   "Writing Introductory and Body Paragraphs", "Creating Monologues and Dialogues"]},
    {"id": "s17", "title": "Conversation and Communication in Context",
     "file": "English-Language_LM_Year-1_Section-17-LV.txt",
     "icon": "🗣️", "color": "#059669",
     "subtopics": ["Effective Communication Skills", "Speech Etiquette and Turn-Taking",
                   "Persuasive and Informative Speaking", "Active Listening and Feedback"]},
    {"id": "s18", "title": "Reading",
     "file": "English-Language_LM_Year-1_Section-18-LV.txt",
     "icon": "📖", "color": "#0D9488",
     "subtopics": ["Reading Techniques — Skimming and Scanning", "Close Reading and Text Analysis",
                   "Comprehension and Interpretation", "Critical Reading Skills"]},
    {"id": "s19", "title": "Subject and Predicate",
     "file": "English-Language_LM_Year-1_Section-19-LV.txt",
     "icon": "📐", "color": "#DC2626",
     "subtopics": ["Understanding the Subject", "Understanding the Predicate",
                   "Types of Sentences by Structure", "Sentence Analysis and Construction"]},
    {"id": "s20", "title": "Text Types and Purposes",
     "file": "English-Language_LM_Year-1_Section-20-LV.txt",
     "icon": "📄", "color": "#65A30D",
     "subtopics": ["Narrative Texts", "Descriptive Texts",
                   "Expository and Persuasive Texts", "Identifying Text Purpose"]},
    {"id": "s21", "title": "Themes",
     "file": "English-Language_LM_Year-1_Section-21-LV.txt",
     "icon": "🎭", "color": "#E11D48",
     "subtopics": ["Understanding Themes in Literature", "Identifying Themes in Texts",
                   "Themes in Poetry and Drama", "Thematic Analysis and Writing"]},
    {"id": "s22", "title": "Ideas",
     "file": "English-Language_LM_Year-1_Section-22-LV.txt",
     "icon": "💡", "color": "#D97706",
     "subtopics": ["Generating Ideas for Writing", "Organising Ideas and Outlining",
                   "Developing Ideas into Paragraphs", "Connecting Ideas Across a Text"]},
    {"id": "s23", "title": "Analysing Non-Fiction Texts",
     "file": "English-Language_LM_Year-1_Section-23-LV.txt",
     "icon": "🔍", "color": "#A21CAF",
     "subtopics": ["Features of Non-Fiction Texts", "Analysing Arguments and Evidence",
                   "Fact vs Opinion in Non-Fiction", "Writing Analytical Responses"]},
    {"id": "s24", "title": "Article Writing",
     "file": "English-Language_LM_Year-1_Section-24-LV.txt",
     "icon": "📰", "color": "#4F46E5",
     "subtopics": ["Structure of an Article", "Writing Engaging Introductions",
                   "Developing Body Paragraphs and Conclusions", "Editing and Publishing Articles"]},
]


def read_text(filepath: str) -> str:
    path = os.path.join(SOURCE_DIR, filepath)
    if not os.path.exists(path):
        return ""
    # Try UTF-8 first, fall back to cp1252 (Windows Western European)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(path, "r", encoding="cp1252") as f:
            return f.read()


def clean_extracted_text(text: str) -> str:
    """Clean PDF extracted text and join fragment lines into paragraphs."""
    # Remove trailing footer content
    for footer in ['ACKNOWLEDGEMENTS', 'List of Contributors', 'REFERENCES']:
        if footer in text:
            text = text[:text.index(footer)]

    lines = text.split('\n')

    # Filter out header/footer noise lines
    clean_lines = []
    for line in lines:
        s = line.strip()
        if s.isdigit() and len(s) <= 3:
            continue
        if s.startswith('SECTION '):
            continue
        if 'English Language' in s and 'Year' in s:
            continue
        if not s or len(s) < 3:
            continue
        clean_lines.append(s)

    # Join fragment lines into paragraphs
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
    """Split paragraphs into roughly equal chunks for lesson creation."""
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
    """Build a single lesson from paragraphs and sub-topic context."""
    lesson_id = f"eng-lang-{section['id']}t{lesson_idx}"
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
            is_activity = any(kw in para_clean.upper() for kw in ["ACTIVITY", "EXERCISE", "TASK"])
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
                    "I understand this well",
                    "I understand most of it",
                    "I need to review the concepts",
                    "I need more explanation"
                ],
                "correctIndex": 0,
                "explanation": "Self-assessment helps identify areas for improvement. Review the concepts and activities if needed."
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
        "subject": "English Language",
        "subjectIcon": section["icon"],
        "programme": "Both",
        "difficulty": min(5, lesson_idx),
        "estimatedMinutes": 10 + lesson_idx * 3,
        "xpReward": 25 + lesson_idx * 5,
        "unitId": "english-language",
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
        return prereqs
    if lesson_idx > 1:
        prereqs.append(f"eng-lang-s{SECTIONS[section_idx - 1]['id']}t{lesson_idx - 1}")
    else:
        prev_section = section_idx - 1
        prev_id = SECTIONS[prev_section - 1]["id"]
        prev_count = len(SECTIONS[prev_section - 1]["subtopics"])
        prereqs.append(f"eng-lang-s{prev_id}t{prev_count}")
    return prereqs


def lesson_to_ts(lesson: dict) -> str:
    """Convert lesson dict to TypeScript source."""
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

    # Steps
    lines.append("    steps: [")
    for step in lesson["steps"]:
        lines.append("      {")
        lines.append(f'        id: {json.dumps(step["id"], ensure_ascii=False)},')
        lines.append(f'        type: {json.dumps(step["type"], ensure_ascii=False)},')
        s = step["content"]
        # Escape backticks in content
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
 * generatedEnglishLessons.ts
 * ────────────────────────────
 * Auto-generated English Language SHS 1 lessons from
 * Ministry of Education curriculum materials.
 *
 * DO NOT EDIT DIRECTLY — re-run scripts/generate_english_lessons.py instead.
 */

import type { Lesson } from './learningContent';

export const ENGLISH_SHS1_LESSONS: Lesson[] = [
'''


def generate_footer() -> str:
    return '''];

export const ENGLISH_SHS1_COUNT = '''


def main():
    print("=" * 60)
    print("  English Language SHS 1 Lesson Generator")
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
