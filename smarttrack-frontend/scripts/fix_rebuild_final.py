#!/usr/bin/env python
"""Final fix for rebuild_coremaths_modules.py - robust approach"""

import re

with open('scripts/rebuild_coremaths_modules.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Strategy: Find lines that are string arguments to info_step/predict_step/etc.
# and change them from '...' to "..." to avoid apostrophe issues.
# 
# Pattern: lines that start with whitespace + ' and contain an apostrophe
# (single quote with letters on both sides)

fixed = 0
new_lines = []
for i, line in enumerate(lines):
    stripped = line.lstrip()
    
    # Check if this is a string argument line: starts with ' after whitespace
    # and is a content/pattern/question/explanation string
    if stripped.startswith("'") and not stripped.startswith("'''"):
        # Count single quotes on this line  
        quote_positions = [j for j, c in enumerate(line) if c == "'"]
        
        if len(quote_positions) >= 2:
            first_q = quote_positions[0]
            last_q = quote_positions[-1]
            
            # Get the string content
            content = line[first_q+1:last_q]
            
            # Check if content has potential apostrophes (letter'letter)
            has_apostrophe = False
            for k in range(1, len(content)):
                if content[k] == "'" and k > 0 and k < len(content)-1:
                    if content[k-1].isalpha() and content[k+1].isalpha():
                        has_apostrophe = True
                        break
            
            if has_apostrophe:
                # Check if content has double quotes - if so, use triple quotes
                if '"' in content:
                    # Use triple-double-quotes
                    prefix = line[:first_q]
                    suffix = line[last_q+1:]
                    line = prefix + '"""' + content + '"""' + suffix
                else:
                    # Change to double quotes  
                    prefix = line[:first_q]
                    suffix = line[last_q+1:]
                    line = prefix + '"' + content + '"' + suffix
                fixed += 1
    
    new_lines.append(line)

new_content = ''.join(new_lines)

with open('scripts/rebuild_coremaths_modules.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Converted {fixed} string literals from single to double quotes")

# Verify syntax
import ast
try:
    ast.parse(new_content)
    print("No syntax errors!")
except SyntaxError as e:
    print(f"Error at line {e.lineno}: {e.msg}")
    lines2 = new_content.split('\n')
    if e.lineno and e.lineno <= len(lines2):
        print(f"  Line {e.lineno}: {repr(lines2[e.lineno-1][:200])}")
        # Show context
        start = max(0, e.lineno - 3)
        end = min(len(lines2), e.lineno + 2)
        for j in range(start, end):
            marker = '>>>' if j+1 == e.lineno else '   '
            print(f'{marker} {j+1}: {repr(lines2[j][:150])}')
