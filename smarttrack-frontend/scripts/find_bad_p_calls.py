import re

with open('scripts/generate_coremaths.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    stripped = line.strip()
    if re.match(r'^p\(', stripped):
        depth = 0
        text = ''
        for j in range(i, min(i+15, len(lines))):
            text += lines[j]
            for ch in lines[j]:
                if ch == '(':
                    depth += 1
                elif ch == ')':
                    depth -= 1
            if depth == 0:
                break
        
        commas = 0
        d = 0
        in_string = False
        string_char = None
        for ch in text:
            if in_string:
                if ch == '\\':
                    continue
                if ch == string_char:
                    in_string = False
                continue
            if ch in ('"', "'"):
                in_string = True
                string_char = ch
                continue
            if ch == '(':
                d += 1
            elif ch == ')':
                d -= 1
            elif ch == ',' and d == 1:
                commas += 1
        
        num_args = commas + 1
        if num_args != 7:
            print(f'Line {i+1}: p() with {num_args} args (expected 7)')
            short = text[:150].replace('\n', '\\n')
            print(f'  {short}...')
            print()
