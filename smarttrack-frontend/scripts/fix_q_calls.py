#!/usr/bin/env python
"""Fix q() calls that have 7 arguments (extra pattern string) by removing the 3rd arg."""

import re

with open('scripts/generate_coremaths.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

# Find all q() calls that span multiple lines
# For each q() call, check if it has an extra string argument between 
# the content string and the question string (i.e., a pattern arg)

# Strategy: find q( on a line, then track forward to find the call's end
# Count number of standalone strings (not inside []) before the options array

fixes = []
i = 0
while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    
    if 'q("coremath' in stripped and stripped.startswith('q('):
        start_line = i
        
        # Track paren depth to find call end
        depth = 0
        call_lines_idx = []
        for j in range(i, min(i+20, len(lines))):
            call_lines_idx.append(j)
            for ch in lines[j]:
                if ch == '(':
                    depth += 1
                elif ch == ')':
                    depth -= 1
            if depth == 0 and j > i:
                break
        
        # Extract the call text
        call_text = '\n'.join(lines[i:call_lines_idx[-1]+1])
        
        # Count standalone string arguments (not inside [])
        # Strategy: find the options array bracket and count strings before it
        # First, find where the options array [ starts (it's the first [...] after the content)
        
        # Simple approach: count strings and check if there's a pattern
        # Check if the 3rd argument (after content) has a line ending with "xxx",
        # followed by another string beginning with "..."
        
        # Find the options array position
        bracket_pos = call_text.find('  [')
        if bracket_pos >= 0:
            # Get text before the options array
            before_options = call_text[:bracket_pos]
            # Count string literals (quoted) in this section
            strings_before = len(re.findall(r'"([^"]*)"', before_options))
            
            # A correct q() should have 3 strings before options: sid, content, question
            # If there are 4, there's an extra pattern string
            if strings_before >= 4:
                # Found a problematic q() - need to remove the pattern string
                # The pattern string is the 3rd one (index 2 in 0-based)
                # It appears after the content string and before the question string
                
                # Find the pattern string in the actual lines
                # The pattern is the 3rd standalone string argument
                # Let's find all string matches in before_options
                str_matches = list(re.finditer(r'"([^"]*)"', before_options))
                if len(str_matches) >= 4:
                    # str_matches[0] = sid
                    # str_matches[1] = content  
                    # str_matches[2] = pattern (extra - to remove)
                    # str_matches[3] = question
                    pattern_match = str_matches[2]
                    pattern_str = pattern_match.group(0)
                    
                    # The pattern could be on its own line like:   "pattern text",
                    # or it could be on the same line as content or question
                    
                    fixes.append((i, pattern_match.start() - (call_text.find('\n') == -1 and 0 or 0), pattern_str))
    
    i += 1

print(f"Found {len(fixes)} q() calls with extra pattern argument")
for line_num, offset, pattern in fixes:
    print(f"  Line {line_num+1}: {pattern[:80]}...")

# Apply fixes by reading the file and removing the pattern strings
# We need to be more careful - let's fix by finding the exact lines

with open('scripts/generate_coremaths.py', 'r', encoding='utf-8') as f:
    content = f.read()

# For each fix, we need to find and remove the pattern string from the q() call
# The pattern string is between the content and question strings

# Let's use a targeted regex approach
# Find q("....", "....",\n  "PATTERN",\n  "QUESTION", ...
# Change to q("....", "....",\n  "QUESTION", ...

import_count = 0

# For each problematic q() call, find the exact location of the pattern string
# and remove it (along with the trailing comma and newline)

for i in range(len(lines)):
    line = lines[i]
    stripped = line.strip()
    
    if 'q("coremath' in stripped and stripped.startswith('q('):
        start_line = i
        
        # Find the call end
        depth = 0
        end_line = i
        for j in range(i, min(i+20, len(lines))):
            end_line = j
            for ch in lines[j]:
                if ch == '(':
                    depth += 1
                elif ch == ')':
                    depth -= 1
            if depth == 0 and j > i:
                break
        
        # Get call text
        call_lines = lines[i:end_line+1]
        call_text = ''.join(call_lines)
        
        # Find the options array position
        bracket_pos = call_text.find('  [')
        if bracket_pos >= 0:
            before_options = call_text[:bracket_pos]
            strings_before = len(re.findall(r'"([^"]*)"', before_options))
            
            if strings_before >= 4:
                # Find the 3rd string (pattern) - it's str_matches[2]
                str_matches = list(re.finditer(r'"([^"]*)"', before_options))
                if len(str_matches) >= 4:
                    pattern_match = str_matches[2]
                    pattern_start = pattern_match.start()
                    pattern_end = pattern_match.end()
                    
                    # Find which line the pattern is on within call_lines
                    # Need to find the character offset within call_text
                    
                    # Find the ", " or ",\n  " after the pattern string
                    # Look for the pattern string followed by comma and optional whitespace/newline
                    after_pattern = call_text[pattern_end:]
                    comma_match = re.match(r'",\s*', after_pattern)
                    
                    if comma_match:
                        # Remove from pattern start to end of comma+whitespace
                        removal_end = pattern_end + comma_match.end()
                        
                        # Build new call text without the pattern
                        new_call = call_text[:pattern_start] + call_text[removal_end:]
                        
                        # Replace the lines
                        full_old = ''.join(call_lines)
                        full_new = new_call
                        
                        if full_old != full_new:
                            content = content.replace(full_old, full_new, 1)
                            import_count += 1
                            print(f"Fixed q() at line {i+1}")

with open('scripts/generate_coremaths.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nTotal fixes applied: {import_count}")

# Verify syntax
import ast
try:
    ast.parse(content)
    print("NO SYNTAX ERRORS!")
except SyntaxError as e:
    print(f"\nERROR at line {e.lineno}: {e.msg}")
    lines_v = content.split('\n')
    if e.lineno:
        start = max(0, e.lineno - 3)
        end = min(len(lines_v), e.lineno + 2)
        for ln in range(start, end):
            marker = '>>>' if ln+1 == e.lineno else '   '
            print(f'{marker} {ln+1}: {repr(lines_v[ln][:200])}')
