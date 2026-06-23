"""Fix all q() calls that have 7 arguments in generate_all_coremaths.py.

The q() function signature is: q(sid, content, question, options, correct, explanation)
Some calls incorrectly have an extra string: q(sid, content, question, EXTRA, options, correct, explanation)
This script finds those and removes the extra string.
"""

import re

with open('scripts/generate_all_coremaths.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Strategy: Find each q() call, extract its inner text, count top-level args
# If there are 7+ args, the 4th one (index 3) is the extra string that needs removal.

fixes = []
i = 0
while i < len(lines):
    stripped = lines[i].strip()
    if stripped.startswith('q(') and len(stripped) > 4 and stripped[2] == '"':
        # Found start of q() call. Find the matching closing paren.
        depth = 0
        in_single = False
        in_double = False
        escaped = False
        start_line = i
        end_line = i
        
        for j in range(i, len(lines)):
            for c in lines[j]:
                if escaped:
                    escaped = False
                    continue
                if c == '\\':
                    escaped = True
                    continue
                if c == "'" and not in_double:
                    in_single = not in_single
                elif c == '"' and not in_single:
                    in_double = not in_double
                elif not in_single and not in_double:
                    if c == '(':
                        depth += 1
                    elif c == ')':
                        depth -= 1
                        if depth == 0:
                            end_line = j
                            break
            if depth == 0:
                break
        
        # Now parse the q() arguments by joining everything between q( and )
        inner_lines = lines[start_line:end_line+1]
        inner_text = ''.join(inner_lines)
        # Remove 'q(' prefix and ')' suffix
        paren_start = inner_text.index('(')
        paren_end = inner_text.rindex(')')
        inner = inner_text[paren_start+1:paren_end].strip()
        
        # Now split into top-level arguments respecting strings and brackets
        args = []
        current = ''
        depth = 0
        in_str = None
        escaped = False
        
        for c in inner:
            if escaped:
                current += c
                escaped = False
                continue
            if c == '\\':
                current += c
                escaped = True
                continue
            if in_str:
                current += c
                if c == in_str:
                    in_str = None
                    args.append(current)
                    current = ''
                continue
            if c in ('"', "'"):
                if current.strip():
                    args.append(current.strip())
                    current = ''
                in_str = c
                current = c
                continue
            if c in '([{':
                depth += 1
                current += c
                continue
            if c in ')]}':
                depth -= 1
                current += c
                if depth == 0 and current.strip():
                    args.append(current.strip())
                    current = ''
                continue
            if c == ',' and depth == 0:
                if current.strip():
                    args.append(current.strip())
                current = ''
                continue
            current += c
        
        if current.strip():
            args.append(current.strip())
        
        # Check: if args[2] is a string and args[3] is also a string, we have 7 args
        # Valid:  ["...", "...", "...", [...], 0, "..."]  = 6 args (indices 0-5)
        # Invalid: ["...", "...", "...", "...", [...], 0, "..."] = 7 args (indices 0-6)
        if len(args) >= 4:
            arg2 = args[2].strip()
            arg3 = args[3].strip()
            if arg2.startswith('"') and arg3.startswith('"'):
                print(f"FOUND 7-arg q() at lines {start_line+1}-{end_line+1}")
                print(f"  Extra arg: {arg3[:60]}...")
                fixes.append((start_line, end_line, args))
        
        i = end_line + 1
    else:
        i += 1

print(f"\nTotal: {len(fixes)} q() calls with 7 arguments to fix")

# Now fix each one
if fixes:
    # Work backwards to preserve line numbers
    for start_line, end_line, args in reversed(fixes):
        # The extra string is args[3] (the 4th arg)
        # We need to find and remove it from the file
        # Strategy: find the line containing args[3] and blank it out
        extra_str = args[3]
        
        for li in range(start_line, end_line + 1):
            if extra_str.strip() in lines[li]:
                print(f"  Removing extra arg from line {li+1}: {lines[li].strip()[:60]}...")
                # Remove this string and its trailing comma from the line
                # Option 1: If the line is just this string plus comma, blank it
                # Option 2: If it's on a line with other stuff, remove just the string+comma
                line_text = lines[li]
                # Check if the line is just "  \"extra_string\","
                pattern = re.compile(r'^\s*"[^"]*",?\s*$')
                if pattern.match(line_text):
                    lines[li] = '\n'  # blank the line
                else:
                    # Remove the extra string from the line
                    # The string might be "something", - with trailing comma
                    lines[li] = lines[li].replace(extra_str + ',', '')
                    lines[li] = lines[li].replace(extra_str, '')
                break
    
    # Write the fixed content
    with open('scripts/generate_all_coremaths.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"Fixed {len(fixes)} q() calls. Written to scripts/generate_all_coremaths.py")
