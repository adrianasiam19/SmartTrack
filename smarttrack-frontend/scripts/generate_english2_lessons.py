"""Generate English Language SHS 2 lessons from extracted PDF text.

Usage: python scripts/generate_english2_lessons.py
Output: app/lib/generatedEngLang2Lessons.ts
"""
import re, os

TEXT_PATH = r"C:\Users\Admin\Downloads\English-Language Year2.txt"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "app", "lib", "generatedEngLang2Lessons.ts")

with open(TEXT_PATH, "r", encoding="utf-8", errors="replace") as f:
    text = f.read()

lines = text.split("\n")

# Section start lines (first "\fYear 2 SECTION N" occurrence in the content)
LINE_MARKERS = {
    1: 101,   # SECTION 1 DIPHTHONGS AND READING COMPREHENSION
    2: 463,   # SECTION 2 SUBORDINATE CLAUSE, PARAGRAPH COHERENCE AND POETRY
    3: 651,   # SECTION 3 Triphthongs, Question Types and Clauses
    4: 816,   # SECTION 4 Noun Clause, Cohesive Devices and Poetry Appreciation
    5: 956,   # SECTION 5 Affricates and Approximants, Grammatical Structures and Clauses
    6: 1101,  # SECTION 6 Relative/Adjectival Clause, Essay and Poetry
    7: 1252,  # SECTION 7 Consonant Clusters, Reading and Adverbial Clause
    8: 1473,  # SECTION 8 Adverbial Clause, Narrative Writing and Poetry
    9: 1611,  # SECTION 9 consonant clusters, reading fluently and subject-verb agreement
    10: 1793, # SECTION 10 subject-verb agreement, speech writing and imAGERY
    11: 1967, # SECTION 11 ORAL narrative, summary writing and subject-verb agreement
    12: 2166, # SECTION 12 ACTIVE AND PASSIVE VOICE, SPEECH WRITING AND IMAGERY
    13: 2542, # SECTION 13 STRESS,INTONATION AND MEANING, ACTIVE VOICE AND SUMMARY WRITING
    14: 2872, # SECTION 14 CUES IN COMMUNICATION, REGISTERS AND SPEECH WRITING
    15: 3131, # SECTION 15 CULTURAL PERSPECTIVE IN COMMUNICATION AND VOCABULARY IN CONTEXT
    16: 3425, # SECTION 16 MINUTES WRITING
    17: 3524, # SECTION 17 REPORT WRITING
    18: 3639, # SECTION 18 SYNONYMS
    19: 3778, # SECTION 19 ANTONYMS
    20: 4099, # SECTION 20 ARTICLE WRITING
    21: 4206, # SECTION 21 RESEARCH AND PRESENTATION
    22: 4324, # SECTION 22 WORD COLLOCATIONS
    23: 4440, # SECTION 23 FORMAL LETTER WRITING
    24: 4555, # SECTION 24 RESEARCH AND PRESENTATION
}

SECTIONS = [
    {"id": "s2e1",  "title": "Diphthongs and Reading Comprehension", "line": 101},
    {"id": "s2e2",  "title": "Subordinate Clause, Paragraph Coherence and Poetry", "line": 463},
    {"id": "s2e3",  "title": "Triphthongs, Question Types and Clauses", "line": 651},
    {"id": "s2e4",  "title": "Noun Clause, Cohesive Devices and Poetry Appreciation", "line": 816},
    {"id": "s2e5",  "title": "Affricates and Approximants, Grammatical Structures and Clauses", "line": 956},
    {"id": "s2e6",  "title": "Relative/Adjectival Clause, Essay and Poetry", "line": 1101},
    {"id": "s2e7",  "title": "Consonant Clusters, Reading and Adverbial Clause", "line": 1252},
    {"id": "s2e8",  "title": "Adverbial Clause, Narrative Writing and Poetry", "line": 1473},
    {"id": "s2e9",  "title": "Consonant Clusters, Reading Fluently and Subject-Verb Agreement", "line": 1611},
    {"id": "s2e10", "title": "Subject-Verb Agreement, Speech Writing and Imagery", "line": 1793},
    {"id": "s2e11", "title": "Oral Narrative, Summary Writing and Subject-Verb Agreement", "line": 1967},
    {"id": "s2e12", "title": "Active and Passive Voice, Speech Writing and Imagery", "line": 2166},
    {"id": "s2e13", "title": "Stress, Intonation and Meaning, Active Voice and Summary Writing", "line": 2542},
    {"id": "s2e14", "title": "Cues in Communication, Registers and Speech Writing", "line": 2872},
    {"id": "s2e15", "title": "Cultural Perspective in Communication and Vocabulary in Context", "line": 3131},
    {"id": "s2e16", "title": "Minutes Writing", "line": 3425},
    {"id": "s2e17", "title": "Report Writing", "line": 3524},
    {"id": "s2e18", "title": "Synonyms", "line": 3639},
    {"id": "s2e19", "title": "Antonyms", "line": 3778},
    {"id": "s2e20", "title": "Article Writing", "line": 4099},
    {"id": "s2e21", "title": "Research and Presentation", "line": 4206},
    {"id": "s2e22", "title": "Word Collocations", "line": 4324},
    {"id": "s2e23", "title": "Formal Letter Writing", "line": 4440},
    {"id": "s2e24", "title": "Research and Presentation", "line": 4555},
]

SUBTOPICS_PER_SECTION = 4

def line_to_pos(line_num: int) -> int:
    """Convert 1-based line number to character position."""
    return sum(len(l) + 1 for l in lines[:line_num - 1])

def clean_text(t: str) -> str:
    t = t.replace("\x0c", " ")
    t = re.sub(r"\n\s*\n\s*\n+", "\n\n", t)
    return t.strip()

def extract_lessons(sec_text: str, num_lessons: int = 4) -> list[str]:
    sec_text = clean_text(sec_text)
    if not sec_text:
        return [f"Lesson content for this section."] * num_lessons

    sec_lines = sec_text.split("\n")
    # Find lesson-like boundaries
    boundaries = [0]
    for idx, line in enumerate(sec_lines):
        s = line.strip()
        if re.match(r"Activity\s+\d+\.\d+", s):
            boundaries.append(idx)
        elif re.match(r"Example\s+\d+", s) and idx > 5:
            boundaries.append(idx)
        elif re.match(r"Exercise\s+\d+", s):
            boundaries.append(idx)
        elif s.upper().startswith("REVIEW QUESTION"):
            boundaries.append(idx)
        elif s.upper().startswith("SUMMARY"):
            boundaries.append(idx)
    boundaries = sorted(set(boundaries))

    if len(boundaries) < 2:
        chunk_size = max(1, len(sec_lines) // num_lessons)
        lessons = []
        for i in range(num_lessons):
            chunk = "\n".join(sec_lines[i * chunk_size:(i + 1) * chunk_size])
            lessons.append(chunk.strip()[:1500])
        return lessons

    chunks = []
    for i in range(len(boundaries)):
        start = boundaries[i]
        end = boundaries[i + 1] if i + 1 < len(boundaries) else len(sec_lines)
        chunk = "\n".join(sec_lines[start:end]).strip()
        if chunk:
            chunks.append(chunk)

    if len(chunks) < num_lessons:
        remaining = "\n".join(sec_lines[boundaries[-1]:]) if boundaries else sec_text
        while len(chunks) < num_lessons:
            chunks.append(remaining[:1500])
    elif len(chunks) > num_lessons:
        while len(chunks) > num_lessons:
            merged = chunks[-2] + "\n\n" + chunks[-1]
            chunks = chunks[:-2] + [merged]

    return [c[:1500] for c in chunks[:num_lessons]]

def lesson_to_ts(lesson_id: str, title: str, content: str, idx: int) -> str:
    content_clean = content.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    content_clean = content_clean.replace("\n", "\\n").replace("\r", "")
    if len(content_clean) > 5000:
        content_clean = content_clean[:5000] + "..."
    difficulty = min(5, max(1, (idx % 5) + 1))
    xp = 20 + (idx * 5)

    return f"""  {{
    id: "{lesson_id}",
    title: `{title}`,
    subject: "English Language",
    subjectIcon: "\\U0001f4d6",
    programme: "Both",
    unitId: "core-english",
    difficulty: {difficulty},
    estimatedMinutes: {15 + (idx % 3) * 5},
    xpReward: {xp},
    prerequisites: [],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {{
        id: "{lesson_id}-content",
        type: "info",
        content: `{content_clean}`
      }}
    ]
  }}"""

def generate():
    lessons = []
    lesson_index = 0

    for sec in SECTIONS:
        start_pos = line_to_pos(sec["line"])
        # Find end: next section or end of file
        sec_idx = SECTIONS.index(sec)
        if sec_idx + 1 < len(SECTIONS):
            end_pos = line_to_pos(SECTIONS[sec_idx + 1]["line"])
        else:
            end_pos = len(text)

        sec_text = text[start_pos:end_pos]
        lesson_texts = extract_lessons(sec_text, SUBTOPICS_PER_SECTION)

        for li, lt in enumerate(lesson_texts):
            lesson_index += 1
            lesson_id = f"eng-lang2-{sec['id']}t{li + 1}"
            title = f"{sec['title']} — Lesson {li + 1}"
            lessons.append(lesson_to_ts(lesson_id, title, lt, lesson_index))

    ts_content = f"""// Auto-generated from English Language SHS 2 document
// Sections: {len(SECTIONS)} | Lessons: {len(lessons)}
import {{ Lesson }} from './learningContent';

export const ENG_LANG2_SHS2_LESSONS: Lesson[] = [
{',\n'.join(lessons)}
];
"""

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(ts_content)

    print(f"OK: Generated {len(lessons)} lessons across {len(SECTIONS)} sections")
    for sec in SECTIONS:
        start_pos = line_to_pos(sec["line"])
        sec_idx = SECTIONS.index(sec)
        end_pos = line_to_pos(SECTIONS[sec_idx + 1]["line"]) if sec_idx + 1 < len(SECTIONS) else len(text)
        size_kb = (end_pos - start_pos) / 1024
        print(f"   {sec['id']}: {sec['title']} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    generate()
