#!/usr/bin/env python
"""
fix_extra_brackets.py — Removes extra ] brackets that appear right after
closing single quotes in function call arguments.

The bug is that some string arguments in question_step(), predict_step(), etc.
end with .'], instead of .'),  — the ] is extra and causes Python syntax errors.
"""
import re

filepath = 'scripts/rebuild_coremaths_modules.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all instances where a line ends with:
#   some_text.'],\n
# or where '.'], appears (any char followed by '],)
# Change to: some_text.'),\n

# Pattern: a character followed by '], — the ] is the extra bracket
# This specifically targets the pattern inside function calls like:
#   question_step(..., 'text.'],

# Strategy: Find all '], where '] immediately follows a closing quote
# and replace with '),

# Count occurrences
count_before = len(re.findall(r"[a-zA-Z0-9)]'\]", content))
print(f"Found {count_before} occurrences of char + '] (checking)")

# Replace ALL occurrences of .'], with .'),
# This is safe because .'], never appears legitimately in Python code
# (list definitions use ['item', ...], not .'],)
new_content = content.replace(".'],", ".'),")

changes = 0
for i, (a, b) in enumerate(zip(content.split('\n'), new_content.split('\n'))):
    if a != b:
        changes += 1

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"\nFixed {changes} lines (changed .'], → .'),)")

# Verify syntax
import ast
try:
    ast.parse(new_content)
    print("✅ NO SYNTAX ERRORS - script is valid Python!")
except SyntaxError as e:
    print(f"\n❌ Remaining error at line {e.lineno}: {e.msg}")
    lines = new_content.split('\n')
    if e.lineno:
        start = max(0, e.lineno - 3)
        end = min(len(lines), e.lineno + 2)
        for i in range(start, end):
            marker = '>>>' if i+1 == e.lineno else '   '
            print(f'{marker} {i+1}: {lines[i][:200]}')
