#!/usr/bin/env python
"""Fix apostrophe issues in rebuild_coremaths_modules.py by converting
single-quoted strings containing apostrophes to double-quoted strings."""

import re

FILEPATH = 'scripts/rebuild_coremaths_modules.py'

with open(FILEPATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Strategy: Find all Python string literals that contain apostrophes
# and are delimited by single quotes. Convert those to double-quoted strings.
#
# Pattern match: '...' where ... contains an apostrophe (like "WASSCE's")
# This regex looks for single-quoted strings containing an apostrophe

def fix_apostrophe_string(match):
    """Convert a single-quoted string containing an apostrophe to double-quoted."""
    full_match = match.group(0)
    inner = match.group(1)  # content between quotes
    # Escape any double quotes that are inside the string
    inner = inner.replace('"', '\\"')
    return f'"{inner}"'

# Match single-quoted strings that contain at least one apostrophe
# The pattern: quote, then any chars including apostrophes, then quote
# But we need to be careful not to match too greedily
pattern = r"'([^']*'[^']*)'"

count_before = len(re.findall(pattern, content))
content = re.sub(pattern, fix_apostrophe_string, content)
count_after = len(re.findall(pattern, content))

print(f"Pattern matches before fix: {count_before}")
print(f"Pattern matches after fix: {count_after}")
print(f"Lines fixed: {count_before - count_after}")

# Write fixed content
with open(FILEPATH, 'w', encoding='utf-8') as f:
    f.write(content)

# Verify syntax
import ast
try:
    ast.parse(content)
    print("\n✅ NO SYNTAX ERRORS - script is valid Python!")
except SyntaxError as e:
    print(f"\n❌ ERROR at line {e.lineno}: {e.msg}")
    lines = content.split('\n')
    if e.lineno:
        start = max(0, e.lineno - 3)
        end = min(len(lines), e.lineno + 2)
        for i in range(start, end):
            marker = '>>>' if i+1 == e.lineno else '   '
            print(f'{marker} {i+1}: {repr(lines[i][:200])}')
