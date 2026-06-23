"""Find ALL q() calls and check argument count."""

with open('scripts/generate_all_coremaths.py', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# Simple approach: find line start of each q( call, then find matching )
i = 0
while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    
    # Check if this line starts a function call q(...)
    if stripped.startswith('q(') and ('"coremath' in stripped or "'coremath" in stripped):
        # Find the matching closing paren across lines
        depth = 0
        j = i
        while j < len(lines):
            for c in lines[j]:
                if c == '(':
                    depth += 1
                elif c == ')':
                    depth -= 1
                    if depth == 0:
                        break
            if depth == 0:
                break
            j += 1
        
        # Join the call text and parse
        call_text = '\n'.join(lines[i:j+1])
        
        # Remove q( and outer )
        inner = call_text[2:-1].strip()
        
        # Count top-level commas
        depth = 0
        commas = 0
        in_single = False
        in_double = False
        for c in inner:
            if c == "'" and not in_double:
                in_single = not in_single
            elif c == '"' and not in_single:
                in_double = not in_double
            elif not in_single and not in_double:
                if c in '([':
                    depth += 1
                elif c in ')]':
                    depth -= 1
                elif c == ',' and depth == 0:
                    commas += 1
        
        nargs = commas + 1
        if nargs != 6:
            print(f'Line {i+1}: q() has {nargs} args (expected 6)')
            for k in range(i, min(j+1, i+8)):
                print(f'  {k+1}: {lines[k].rstrip()}')
            print()
        
        i = j  # Skip to end of this call
    
    i += 1
