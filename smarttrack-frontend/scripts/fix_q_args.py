"""Fix all q() calls that have 7 arguments instead of 6 by merging the extra hint."""
import re

with open('scripts/generate_all_coremaths.py', 'r', encoding='utf-8') as f:
    content = f.read()

# We need to find q(..."coremath... calls with 7 args.
# Pattern: The 4th arg (index 3) is a standalone string like "x = ?" that should be merged into arg 3.

# Strategy: find q("coremath  calls, then find the next 2 string args in a row before a list.

result = []
lines = content.split('\n')
i = 0
fixed_count = 0

while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    
    # Check if this line starts a q("coremath call
    if stripped.startswith('q("coremath') or stripped.startswith("q('coremath"):
        # Find the full extent of this q() call
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
        
        # Get the full q() call text
        q_text = '\n'.join(lines[i:j+1])
        
        # Count top-level commas (not inside strings or brackets)
        depth = 0
        commas = []
        in_str = False
        sc = None
        for idx, c in enumerate(q_text[2:-1]):  # skip 'q(' and last ')'
            if in_str:
                if c == '\\':
                    continue
                if c == sc:
                    in_str = False
            else:
                if c in ['"', "'"]:
                    in_str = True
                    sc = c
                elif c in '([':
                    depth += 1
                elif c in ')]':
                    depth -= 1
                elif c == ',' and depth == 0:
                    commas.append(idx)
        
        nargs = len(commas) + 1
        
        if nargs == 7:
            # The extra arg is at position 3 (0-indexed), which is the 4th argument
            # We need to find its exact position in the text
            arg3_start = commas[2] + 1  # start of arg 3 (string)
            arg4_start = commas[3] + 1  # start of arg 4 (extra string)
            arg4_end = commas[4]  # end of arg 4, before options
            
            arg3 = q_text[2:-1][arg3_start:arg3_start + 100].strip()
            arg4 = q_text[2:-1][arg4_start:arg4_start + 100].strip()
            
            # Extract the two string values
            arg3_val = arg3.strip().rstrip(',')
            arg4_val = arg4.strip().rstrip(',')
            
            if arg3_val and arg4_val:
                # Merge: replace ", arg4" with empty string
                # The comma between arg3 and arg4 is at index arg4_start - 1
                before_extra = q_text[2:-1][:arg4_start - 1].rstrip()
                after_extra = q_text[2:-1][arg4_end:]
                
                # Merge the values
                # Remove quotes from both strings
                q3 = arg3_val
                if q3.startswith('"') and q3.endswith('"'):
                    q3 = q3[1:-1]
                elif q3.startswith("'") and q3.endswith("'"):
                    q3 = q3[1:-1]
                
                q4 = arg4_val
                if q4.startswith('"') and q4.endswith('"'):
                    q4 = q4[1:-1]
                elif q4.startswith("'") and q4.endswith("'"):
                    q4 = q4[1:-1]
                
                # Rebuild: remove the comma, space, and arg4
                # Find the last comma before arg4
                inner = q_text[2:-1]
                comma_before_arg4 = inner.rfind(',', 0, arg4_start - 1)
                if comma_before_arg4 >= 0:
                    new_inner = inner[:comma_before_arg4] + ',\n          ' + repr(q3 + ', ' + q4) + inner[arg4_end:]
                    # Actually, just use the inner till arg4_end
                    # But the merged string should be quoted
                    merged = q3 + ', ' + q4
                    new_inner = inner[:comma_before_arg4] + ',\n          ' + f'"{merged}"' + inner[arg4_end:]
                    new_q = 'q(' + new_inner + ')'
                    
                    # Replace lines
                    new_lines = new_q.split('\n')
                    # Put them in place
                    result.extend(new_lines)
                    fixed_count += 1
                    i = j + 1
                    continue
    
    result.append(line)
    i += 1

with open('scripts/generate_all_coremaths.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(result))

print(f"Fixed {fixed_count} q() calls with 7 arguments.")
