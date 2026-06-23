#!/usr/bin/env python
"""Fix q() calls with 7 arguments. Uses raw line-based editing."""

import re

with open('scripts/generate_coremaths.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# The known problematic lines (0-indexed)
problem_lines = [481, 486, 500, 528, 578, 604, 701, 929, 955, 1105, 1130, 1181, 1205]

total_fixes = 0
for pl in problem_lines:
    # Read the q() call
    line = lines[pl]
    # This line starts q("id", "content", ...
    # The pattern is the 3rd arg - it's on the same line or the next line
    
    # Strategy: find where the pattern string is and remove it
    # The pattern always ends with a comma followed by newline or space
    # followed by the question string
    
    # Find the first 3 strings in this call
    call_text = ''.join(lines[pl:pl+20])  # enough for the full call
    
    # Find strings before the options bracket
    bracket_idx = -1
    in_str = False
    for idx, ch in enumerate(call_text):
        if ch == '"':
            in_str = not in_str
        if not in_str and ch == '[':
            bracket_idx = idx
            break
    
    if bracket_idx < 0:
        continue
    
    before_br = call_text[:bracket_idx]
    str_matches = list(re.finditer(r'"[^"]*"', before_br))
    
    if len(str_matches) < 4:
        continue  # Not a problematic one
    
    # Get the exact text of the pattern string (3rd match, index 2)
    pm = str_matches[2]
    pat_start = pm.start()
    pat_end = pm.end()
    
    # Find what comes after the pattern
    after_pat = call_text[pat_end:]
    comma_match = re.match(r',\s*', after_pat)
    if not comma_match:
        continue
    
    removal_end = pat_end + comma_match.end()
    
    # Get the old and new text
    old_text = call_text[:removal_end] + call_text[removal_end:]  # full original
    old_first_part = call_text[:pat_start]  # before pattern
    old_second_part = call_text[removal_end:]  # after pattern and comma
    new_text = old_first_part + old_second_part
    
    # The first part of call_text (up to removal_end) is what changes
    old_changed = call_text[:pat_start] + call_text[pat_start:removal_end]
    new_changed = call_text[:pat_start] + ''  # Just remove pattern+comma
    # Actually: old_changed = first_part + pattern + comma_ws
    # new_changed = first_part
    
    old_pattern_txt = call_text[pat_start:removal_end]
    
    # Replace this occurrence in the file content
    with open('scripts/generate_coremaths.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if old_pattern_txt in content:
        content = content.replace(old_pattern_txt, '', 1)
        total_fixes += 1
        print(f"Fixed: removed '{pm.group()[:50]}...'")
        with open('scripts/generate_coremaths.py', 'w', encoding='utf-8') as f:
            f.write(content)
    else:
        print(f"Could not find pattern at line {pl+1}: {repr(old_pattern_txt[:80])}")

print(f"\nTotal fixes: {total_fixes}")
