#!/usr/bin/env python
"""Fix q() calls that have 7 arguments by removing the extra pattern string (3rd arg)."""

import re

with open('scripts/generate_coremaths.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
total_fixes = 0

for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith('q("coremath'):
        # Find the full q() call
        depth = 0
        call_start = i
        call_end = i
        for j in range(i, min(i+20, len(lines))):
            call_end = j
            for ch in lines[j]:
                if ch == '(':
                    depth += 1
                elif ch == ')':
                    depth -= 1
            if depth == 0 and j > i:
                break
        
        call_lines = lines[call_start:call_end+1]
        call_text = ''.join(call_lines)
        
        # Find where the options array starts (the first [ not inside a string)
        bracket_idx = -1
        in_str = False
        for idx, ch in enumerate(call_text):
            if ch == '"':
                in_str = not in_str
            if not in_str and ch == '[':
                bracket_idx = idx
                break
        
        if bracket_idx >= 0:
            before_br = call_text[:bracket_idx]
            str_count = len(re.findall(r'"[^"]*"', before_br))
            
            if str_count > 3:
                # Find the 3rd string - this is the pattern to remove
                str_matches = list(re.finditer(r'"[^"]*"', before_br))
                if len(str_matches) >= 4:
                    pattern_str = str_matches[2]  # index 2 = 3rd match (0-based)
                    p_start = pattern_str.start()
                    p_end = pattern_str.end()
                    
                    # Find the comma and whitespace after the pattern string
                    after_pattern = call_text[p_end:]
                    comma_match = re.match(r',\s*', after_pattern)
                    if comma_match:
                        # Calculate removal range
                        removal_end = p_end + comma_match.end()
                        
                        # Build new call text without the pattern
                        new_call = call_text[:p_start] + call_text[removal_end:]
                        
                        # Replace full_old with full_new in content
                        if call_text in content:
                            content = content.replace(call_text, new_call, 1)
                            total_fixes += 1
                            print(f"Fixed line {i+1} ({str_matches[0].group()[:40]}...)")

with open('scripts/generate_coremaths.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nTotal fixes applied: {total_fixes}")

# Verify can execute
try:
    exec(compile(content, 'generate_coremaths.py', 'exec'))
    print("SUCCESS: Script executes without errors!")
except TypeError as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
except SyntaxError as e:
    print(f"SYNTAX ERROR at line {e.lineno}: {e.msg}")
