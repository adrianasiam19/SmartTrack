#!/usr/bin/env python
"""
fix_script_strings.py
─────────────────────
Rebuilds the script content using triple-quoted strings for all
content arguments to avoid apostrophe escaping issues.
"""

import re

filepath = 'scripts/rebuild_coremaths_modules.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# The strategy: use a simple state machine to identify Python string literals
# that are function arguments to info_step, predict_step, etc., and convert
# them from single-quoted to triple-double-quoted.

lines = content.split('\n')
new_lines = []
i = 0

# Track whether we're inside a string argument that needs conversion
in_content_arg = False
current_lines = []
depth = 0  # parentheses depth

step_funcs = ('info_step(', 'predict_step(', 'question_step(', 'checkpoint_step(', 'make_lesson(')

while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    
    # Check if this line starts a step function call
    if not in_content_arg:
        for func in step_funcs:
            if func in stripped:
                # Count opening parens
                depth += stripped.count('(') - stripped.count(')')
                current_lines = [line]
                in_content_arg = True
                break
        if not in_content_arg:
            new_lines.append(line)
    else:
        current_lines.append(line)
        depth += stripped.count('(') - stripped.count(')')
        
        if depth <= 0 and line.rstrip().endswith('),'):
            # End of function call - process the block
            block = '\n'.join(current_lines)
            
            # Convert single-quoted strings to triple-quoted strings
            # We need to be careful to only convert the content string arguments,
            # not the step_id strings (which don't have issues)
            
            # Simple approach: find all '...' strings and if they contain
            # a potential apostrophe (letter-quote-letter), convert to triple quotes
            def fix_string(match):
                s = match.group(1)
                # Check if this string contains a potential apostrophe
                # i.e., a ' that has letters on both sides
                has_apostrophe = False
                for j in range(1, len(s) - 1):
                    if s[j] == "'" and s[j-1].isalpha() and s[j+1].isalpha():
                        has_apostrophe = True
                        break
                
                if has_apostrophe:
                    # Convert to triple-double-quoted string
                    # But check if the string already has """
                    if '"""' in s:
                        return match.group(0)  # skip if would break
                    return '"""' + s + '"""'
                return match.group(0)
            
            # Only process the 2nd+ arguments (skip the step_id)
            # Find the first string literal (step_id), skip it
            # then process subsequent string literals
            
            # Actually, simpler: just process ALL string literals in the block
            # that contain apostrophes
            block = re.sub(r"'((?:[^'\\]|\\.)*)'", fix_string, block)
            
            new_lines.append(block)
            in_content_arg = False
            current_lines = []
            depth = 0
            i += 1
            continue
    
    i += 1

# If still in content arg at end of file, just append what we have
if in_content_arg:
    new_lines.append('\n'.join(current_lines))

new_content = '\n'.join(new_lines)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Conversion complete. Checking syntax...")

# Verify syntax
try:
    compile(new_content, filepath, 'exec')
    print("✅ No syntax errors!")
except SyntaxError as e:
    print(f"❌ Syntax error at line {e.lineno}: {e.msg}")
    lines_list = new_content.split('\n')
    if e.lineno and e.lineno <= len(lines_list):
        print(f"   Line content: {repr(lines_list[e.lineno-1][:200])}")
