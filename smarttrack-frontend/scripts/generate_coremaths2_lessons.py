"""Generate Core Mathematics SHS 2 lessons from extracted PDF text.

Usage: python scripts/generate_coremaths2_lessons.py
Output: app/lib/generatedCoreMaths2Lessons.ts
"""
import re, json, os

TEXT_PATH = r"C:\Users\Admin\Downloads\Core Maths year 2.txt"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "app", "lib", "generatedCoreMaths2Lessons.ts")

with open(TEXT_PATH, "r", encoding="utf-8", errors="replace") as f:
    text = f.read()

# Section definitions: (id, title, subtitle, start_marker, start_offset, end_marker, end_offset)
# We locate markers from the raw text
SECTIONS = [
    {
        "id": "m1",
        "title": "Number Sets",
        "subtitle": "Real Number and Numeration System",
        "start": 0,
        "end": 0,
    },
    {
        "id": "m2",
        "title": "Equations and Inequalities",
        "subtitle": "Applications of Expressions, Equations and Inequalities",
        "start": 0,
        "end": 0,
    },
    {
        "id": "m3",
        "title": "Rigid Motion",
        "subtitle": "Spatial Sense",
        "start": 0,
        "end": 0,
    },
    {
        "id": "m4",
        "title": "Data Collection, Organisation and Representation",
        "subtitle": "Statistical Reasoning and its Application in Real Life",
        "start": 0,
        "end": 0,
    },
    {
        "id": "m5",
        "title": "Ratios, Rates and Proportions",
        "subtitle": "Proportional Reasoning",
        "start": 0,
        "end": 0,
    },
    {
        "id": "m6",
        "title": "Patterns and Relations Involving Sequences and Series",
        "subtitle": "Patterns and Relationships",
        "start": 0,
        "end": 0,
    },
    {
        "id": "m7",
        "title": "Surface Areas and Volumes",
        "subtitle": "Measurement",
        "start": 0,
        "end": 0,
    },
    {
        "id": "m8",
        "title": "Working with Data and Probability Experiments",
        "subtitle": "Statistical and Probability Reasoning and their Application in Real Life",
        "start": 0,
        "end": 0,
    },
    {
        "id": "m9",
        "title": "Vectors and Trigonometry",
        "subtitle": "Measurement",
        "start": 0,
        "end": 0,
    },
]

# Find section boundaries using double-formfeed markers: \x0c\x0cSECTION N
FF = chr(12)  # form feed character
for i, sec in enumerate(SECTIONS):
    sec_num = i + 1
    marker = f"{FF}{FF}SECTION {sec_num} "
    pos = text.find(marker)
    if pos < 0:
        # Try single form feed
        marker = f"{FF}SECTION {sec_num} "
        pos = text.find(marker)
    if pos < 0:
        # Try just "SECTION N" after TOC (skip first 300 chars to avoid TOC matches)
        marker = f"SECTION {sec_num}"
        pos = text.find(marker, 300)
    sec['start'] = pos

    # End is start of next section
    if i + 1 < len(SECTIONS):
        next_sec_num = i + 2
        next_marker = f"{FF}{FF}SECTION {next_sec_num} "
        end_pos = text.find(next_marker, sec['start'] + 5)
        if end_pos < 0:
            next_marker = f"{FF}SECTION {next_sec_num} "
            end_pos = text.find(next_marker, sec['start'] + 5)
        if end_pos < 0:
            next_marker = f"SECTION {next_sec_num}"
            end_pos = text.find(next_marker, sec['start'] + 5)
        sec['end'] = end_pos if end_pos > 0 else len(text)
    else:
        sec['end'] = len(text)

# Fallback: use line-based positions for any section still not found
missing = [s for s in SECTIONS if s['start'] < 0]
if missing:
    print(f'WARNING: Could not find sections via markers: {[s["title"] for s in missing]}. Using line-based fallback.')
    lines = text.split('\n')
    line_markers = {
        1: 382,
        2: 1075,
        3: 1461,
        4: 1760,
        5: 2482,
        6: 2962,
        7: 3347,
        8: 3808,
        9: 4162,
    }
    for i, sec in enumerate(SECTIONS):
        if sec['start'] >= 0:
            continue
        sec_num = i + 1
        start_line = line_markers.get(sec_num, 0)
        sec['start'] = sum(len(line) + 1 for line in lines[:start_line-1]) if start_line > 0 else 0
        if i + 1 < len(SECTIONS):
            next_start_line = line_markers.get(i + 2, len(lines))
            sec['end'] = sum(len(line) + 1 for line in lines[:next_start_line-1])
        else:
            sec['end'] = len(text)

SUBTOPICS_PER_SECTION = 4

def clean_text(t: str) -> str:
    """Clean up extracted text for lesson content."""
    t = t.replace("\x0c", " ")
    # Remove repetitive headers/footers
    t = re.sub(r"\n\s*\n\s*\n+", "\n\n", t)
    t = t.strip()
    return t

def extract_lessons(sec_text: str, num_lessons: int = 4) -> list[str]:
    """Split section text into lesson-sized chunks."""
    # Remove common headers
    sec_text = clean_text(sec_text)
    if not sec_text:
        return [f"Lesson content for this section."] * num_lessons

    lines = sec_text.split("\n")
    # Find lesson-like boundaries: "Activity X.Y", "Example X.Y", "Exercise", "Summary"
    lesson_boundaries = [0]
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if re.match(r"Activity\s+\d+\.\d+", stripped):
            lesson_boundaries.append(idx)
        elif re.match(r"Example\s+\d+\.\d+", stripped) and idx > 5:
            lesson_boundaries.append(idx)
        elif re.match(r"Exercise\s+\d+", stripped):
            lesson_boundaries.append(idx)
        elif stripped.upper().startswith("SUMMARY") or stripped.upper().startswith("REVIEW"):
            lesson_boundaries.append(idx)

    # Deduplicate and sort
    lesson_boundaries = sorted(set(lesson_boundaries))

    if len(lesson_boundaries) < 2:
        # No clear boundaries — split evenly
        chunk_size = max(1, len(lines) // num_lessons)
        lessons = []
        for i in range(num_lessons):
            chunk = "\n".join(lines[i * chunk_size:(i + 1) * chunk_size])
            lessons.append(chunk.strip()[:1500])
        return lessons

    # Build chunks from boundaries
    chunks = []
    for i in range(len(lesson_boundaries)):
        start = lesson_boundaries[i]
        end = lesson_boundaries[i + 1] if i + 1 < len(lesson_boundaries) else len(lines)
        chunk = "\n".join(lines[start:end]).strip()
        if chunk:
            chunks.append(chunk)

    # Pad or trim to num_lessons
    if len(chunks) < num_lessons:
        # Pad with remaining text
        remaining = "\n".join(lines[lesson_boundaries[-1]:]) if lesson_boundaries else sec_text
        while len(chunks) < num_lessons:
            chunks.append(remaining[:1500])
    elif len(chunks) > num_lessons:
        # Merge excess
        while len(chunks) > num_lessons:
            merged = chunks[-2] + "\n\n" + chunks[-1]
            chunks = chunks[:-2] + [merged]

    return [c[:1500] for c in chunks[:num_lessons]]


def lesson_to_ts(lesson_id: str, title: str, content: str, section_title: str, idx: int) -> str:
    """Generate TypeScript for one lesson object."""
    content_clean = content.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    content_clean = content_clean.replace("\n", "\\n").replace("\r", "")
    # Truncate if too long
    if len(content_clean) > 5000:
        content_clean = content_clean[:5000] + "..."
    difficulty = min(5, max(1, (idx % 5) + 1))
    xp = 20 + (idx * 5)

    return f"""  {{
    id: "{lesson_id}",
    title: `{title}`,
    subject: "Core Mathematics",
    subjectIcon: "\U0001f4d0",
    programme: "Both",
    unitId: "core-maths",
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
        sec_text = text[sec["start"]:sec["end"]] if sec["start"] >= 0 else ""
        lesson_texts = extract_lessons(sec_text, SUBTOPICS_PER_SECTION)

        for li, lt in enumerate(lesson_texts):
            lesson_index += 1
            lesson_id = f"coremath2-s2m{i + 1}t{li + 1}"
            title = f"{sec['title']} — Lesson {li + 1}"
            lessons.append(lesson_to_ts(lesson_id, title, lt, sec["title"], lesson_index))

    ts_content = f"""// Auto-generated from Core Maths SHS 2 document
// Sections: {len(SECTIONS)} | Lessons: {len(lessons)}
import {{ Lesson }} from './learningContent';

export const CORE_MATHS2_SHS2_LESSONS: Lesson[] = [
{',\n'.join(lessons)}
];
"""

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(ts_content)

    print(f"OK: Generated {len(lessons)} lessons across {len(SECTIONS)} sections")
    print(f"   Output: {OUT_PATH}")
    # Print section stats
    for sec in SECTIONS:
        if sec["start"] >= 0 and sec["end"] > sec["start"]:
            size_kb = (sec["end"] - sec["start"]) / 1024
            print(f"   {sec['id']}: {sec['title']} ({size_kb:.0f} KB)")
        else:
            print(f"   {sec['id']}: {sec['title']} (NOT FOUND)")


if __name__ == "__main__":
    generate()
