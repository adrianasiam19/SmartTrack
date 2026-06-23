#!/usr/bin/env python
"""
fix_script_quotes.py
────────────────────
Fixes apostrophes (single quotes) inside Python single-quoted strings
in the rebuild_coremaths_modules.py script.

Strategy: Convert all string arguments to info_step/predict_step/question_step/
checkpoint_step that are single-quoted to double-quoted instead.
"""
import re

filepath = 'scripts/rebuild_coremaths_modules.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# The problematic pattern: single-quoted Python strings containing apostrophes
# like 'Let's start' where ' in "Let's" breaks the string.
#
# Strategy: Find all instances of the pattern:
#   'text...<apostrophe>...text'
# and convert them to:
#   "text...<apostrophe>...text"
#
# A more robust approach: process the file line by line, tracking string state.
# But given the file structure, the simplest fix is to replace all single-quoted
# Python string literals that are function arguments with double-quoted ones.
#
# Even simpler: just find all apostrophes inside single-quoted Python strings
# and escape them.

# The key insight: in the Python source, string arguments to info_step etc.
# start with a single quote at the beginning of a line (after indentation).
# If the line has '...' and there's an unescaped ' in the middle, that's the issue.

# Simpler fix: Replace all apostrophes in the content that appear inside
# Python single-quoted strings. But tracking string state is complex.

# Most pragmatic fix: convert the content strings from single-quoted to
# double-quoted. We can do this safely because NO content string uses
# literal double-quote characters (they use curly quotes or escaped quotes).

lines = content.split('\n')
fixed_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    stripped = line.lstrip()
    
    # Check if this line starts a function argument string
    # Pattern: argument_name('...  or just '... 
    # We look for lines that contain ' followed by text with apostrophes
    
    # Count quotes on this line
    single_quotes = [j for j, c in enumerate(line) if c == "'" and (j == 0 or line[j-1] != '\\')]
    
    # If there's an odd number of unescaped single quotes and the line
    # appears to be a function argument, it likely has an apostrophe issue
    if len(single_quotes) % 2 != 0 and ('content:' in stripped or stripped.startswith("'") or stripped.startswith("        '")):
        # This line likely has a broken string due to apostrophe
        # Replace the outer single quotes with double quotes
        # Find the first and last quote
        first_q = single_quotes[0]
        last_q = single_quotes[-1]
        
        # Check if the content between first and last quote contains double quotes
        # If so, we can't safely convert
        middle = line[first_q+1:last_q]
        if '"' not in middle:
            # Safe to convert
            line = line[:first_q] + '"' + middle + '"' + line[last_q+1:]
            fixed_lines.append(line + '  # FIXED')
            i += 1
            continue
    
    fixed_lines.append(line)
    i += 1

new_content = '\n'.join(fixed_lines)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Fix script applied. Checking syntax...")

# Check syntax
try:
    compile(new_content, 'rebuild_coremaths_modules.py', 'exec')
    print("✅ No syntax errors!")
except SyntaxError as e:
    print(f"❌ Still has error at line {e.lineno}, offset {e.offset}: {e.msg}")
    lines = new_content.split('\n')
    if e.lineno and e.lineno <= len(lines):
        ln = lines[e.lineno - 1]
        print(f"   Line: {repr(ln[:200])}")
