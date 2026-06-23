"""Fix the f-string interpolation for lessons_str in generate_coremaths.py

The issue: line 1383 has `f"{{lessons_str}}\\\n"` which renders the
literal text `{lessons_str}` instead of the variable value because
`{{` and `}}` in f-strings produce literal `{` and `}`.

Fix: replace the line with `+ lessons_str + "\\n"` so the variable
value is concatenated instead.
"""

with open("scripts/generate_coremaths.py", "r", encoding="utf-8") as f:
    content = f.read()

# The problematic line in the file is:
#         f"{{lessons_str}}\\n"
# In f-strings, {{ produces { and }} produces }, so this renders as {lessons_str}\n
# We need to use the variable lessons_str instead

# Find and replace the line
# Look for the pattern: f"{{lessons_str}}\\n" with various escaping
import re

# The line starts with whitespace, then f"{...", ends with "\n"
pattern = r'^(\s+)f"\{\{lessons_str\}\}\\(?:\\n|n)"'
replacement = r'\1+ lessons_str + "\\n"'

lines = content.split("\n")
changed = False
for i, line in enumerate(lines):
    if "lessons_str" in line and "f" in line and "{{" in line:
        new_line = re.sub(pattern, replacement, line, count=1)
        if new_line != line:
            print(f"Fixed line {i+1}:")
            print(f"  Before: {repr(line)}")
            print(f"  After:  {repr(new_line)}")
            lines[i] = new_line
            changed = True
            break

if not changed:
    print("No fix applied. Let me search for alternative patterns...")
    for i, line in enumerate(lines):
        if "lessons_str" in line and ("f" in line or "format" in line):
            print(f"Line {i+1}: {repr(line)}")

if changed:
    with open("scripts/generate_coremaths.py", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\nSUCCESS: Fix applied!")

    # Verify syntax
    with open("scripts/generate_coremaths.py", "r", encoding="utf-8") as f:
        content = f.read()
    try:
        compile(content, "scripts/generate_coremaths.py", "exec")
        print("Syntax check: OK")
    except SyntaxError as e:
        print(f"Syntax error after fix: {e}")
