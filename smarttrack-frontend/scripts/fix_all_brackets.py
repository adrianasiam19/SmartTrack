#!/usr/bin/env python
"""
Fix ALL instances of extra ] brackets in function call arguments.
Pattern: anyChar'],[newline/end] → anyChar'),[newline/end]
where the ] is extra and should be removed.
"""
import ast

filepath = 'scripts/rebuild_coremaths_modules.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Strategy: Find any occurrence of '], and replace with '),
# BUT only when it appears to be inside a function call argument (not in a list)
# We check context: if "']," appears within a line that's inside a function call

# Actually, we need to look at the structure. The issue is:
# A function call like: question_step(..., 'text.'],
# Should be: question_step(..., 'text.'),

# In the generated TS content, the '], at the end of a line closes a JavaScript
# object/array, but in Python this should be '),

# The pattern is specifically: closing quote + bracket + comma
# at places where just closing quote + comma + closing paren is needed.

# Let me find ALL occurrences of "']," in the file and check each one
lines = content.split('\n')

fixes = []
for i, line in enumerate(lines):
    # Find all positions of '], in this line
    start = 0
    while True:
        idx = line.find("'],", start)
        if idx < 0:
            break
        
        # Check context: what follows '], ?
        rest = line[idx+3:]
        
        # If '], is followed by ) or end of line, it might be an info_step/question_step argument
        # If '], is followed by another string like "], '", it's a list element - keep it
        
        # Heuristic: look at what comes before the '
        if idx >= 1:
            before_char = line[idx-1]
            # If the char before ' is alpha/numeric/emoji, this is a string ending
            # If it's a space or [, it's likely a list element
            
            # Check the content AFTER '], 
            # In function calls: after '], there should be ) or \n
            # In lists: after '], there's a space and another string
            
            stripped_rest = rest.lstrip()
            if stripped_rest.startswith(')') or stripped_rest == '' or stripped_rest.startswith('\n'):
                # Function argument - replace '], with '),
                fix_position = idx
                fix_until = idx + 3  # length of "'],"
                
                # Build the replacement
                new_line = line[:fix_position + 1] + '),' + rest
                fixes.append((i+1, fix_position))
                line = new_line
                break  # only fix first occurrence per line
            elif stripped_rest.startswith("'"):
                # List element - keep the ]
                pass
            
            # Also check: the most common case is '], at the very end of a line
            # (possibly with trailing whitespace)
            if rest.strip() == '':
                # Line ends with '], - this should be '),
                line = line[:idx] + "')," + rest[3:]
                fixes.append((i+1, idx))
                break
        
        start = idx + 3

new_content = '\n'.join(lines)

# Also handle the case where '], is followed by nothing (end of line):
import re
# Pattern: '], followed by optional whitespace and end of line
def fix_line_end(match):
    return match.group(0).replace('],', '),')

new_content = re.sub(r"'],\s*$", fix_line_end, new_content, flags=re.MULTILINE)

# Count changes
original_lines = content.split('\n')
new_lines_list = new_content.split('\n')
changes = sum(1 for a, b in zip(original_lines, new_lines_list) if a != b)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Fixed {changes} lines")

# Verify syntax
try:
    ast.parse(new_content)
    print("✅ NO SYNTAX ERRORS")
except SyntaxError as e:
    print(f"\n❌ Error at line {e.lineno}: {e.msg}")
    if e.lineno:
        start = max(0, e.lineno - 2)
        end = min(len(new_lines_list), e.lineno + 1)
        for i in range(start, end):
            marker = '>>>' if i+1 == e.lineno else '   '
            print(f'{marker} {i+1}: {repr(new_lines_list[i][:200])}')
