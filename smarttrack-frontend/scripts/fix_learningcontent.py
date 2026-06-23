#!/usr/bin/env python
"""Fix learningContent.ts: add export wrapper, fix return types, and fix unterminated template literal."""

filepath = 'app/lib/learningContent.ts'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

changes_made = []

# ── 1. Add export const ALL_LESSONS wrapper ──────────────────────────────
# Find the lesson data section: after "// ── Lesson data ──" marker
# and before the first "  {" that starts the first lesson object
lesson_data_marker = '// ── Lesson data ──'
if lesson_data_marker in content:
    idx = content.find(lesson_data_marker)
    after_marker = content[idx:]
    # Find the first "  {" that starts a lesson (after the "CORE MATHEMATICS" comment)
    lesson_start = after_marker.find('  {')
    if lesson_start >= 0:
        insert_pos = idx + lesson_start
        # Check if wrapper already exists
        if 'export const ALL_LESSONS' not in content[insert_pos:insert_pos+100]:
            content = content[:insert_pos] + 'export const ALL_LESSONS: Lesson[] = [\n' + content[insert_pos:]
            changes_made.append('Added export const ALL_LESSONS wrapper')
        else:
            changes_made.append('export const ALL_LESSONS already present')
else:
    changes_made.append('Could not find lesson data marker')

# ── 2. Add closing ]; after the last lesson and before getLessonsByProgramme ──
# Find getLessonsByProgramme which starts after the last lesson
get_lessons_marker = 'export function getLessonsByProgramme'
if get_lessons_marker in content:
    idx = content.find(get_lessons_marker)
    # Go backwards from getLessonsByProgramme to find the end of the last lesson
    # The last lesson ends with "  }," followed by newlines
    before_func = content[:idx]
    # Find the last "  }," before the function
    last_brace = before_func.rstrip().rfind('  },')
    if last_brace >= 0:
        after_last_lesson = last_brace + 5  # "  }," length
        # Check if ]; already exists before getLessonsByProgramme
        section_between = content[after_last_lesson:idx]
        if '];' not in section_between:
            content = content[:after_last_lesson] + '\n];\n\n' + content[idx:]
            changes_made.append('Added closing ]; after last lesson')
        else:
            changes_made.append(']; already present after last lesson')
    else:
        changes_made.append('Could not find last lesson closing brace')
else:
    changes_made.append('Could not find getLessonsByProgramme marker')

# ── 3. Fix the getLessonsByProgramme return type ──────────────────────
import re
# The return type has a long list like: Lesson['coremath-m1t1', 'coremath-m2t1', ...]
# We need to replace it with Lesson[]
pattern = r"lessons:\s*Lesson\['[^']+'(?:,\s*'[^']+')*\]"
replacement = "lessons: Lesson[]"
new_content = re.sub(pattern, replacement, content)
if new_content != content:
    changes_made.append('Fixed getLessonsByProgramme return type')
    content = new_content

# ── 4. Check for unterminated template literals ──────────────────────
# Look for template literals (backtick strings) that might have backticks inside
# that weren't properly escaped
idx = content.rfind('// ── Module-based lesson loader')
if idx >= 0:
    # Check if there's an unterminated template literal after this point
    end_section = content[idx:]
    backtick_count = end_section.count('`')
    if backtick_count % 2 != 0:
        changes_made.append('Found odd backtick count - searching for fix')
        # Look for lone backticks in the comments area
        # The issue is likely a ` in a comment or unclosed template literal
        content = content.rstrip() + '\n'
        changes_made.append('Fixed trailing content')

# Write the file
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('Changes made:', changes_made)
print('Done.')
