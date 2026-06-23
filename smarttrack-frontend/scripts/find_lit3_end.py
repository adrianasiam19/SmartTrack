import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('app/lib/learningContent.ts', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find lit-3 end (before the History section)
in_lit3 = False
after_lit3_line = 0
for i, line in enumerate(lines):
    if "id: 'lit-3'" in line:
        in_lit3 = True
    if in_lit3 and line.strip() == '],':
        after_lit3_line = i + 1  # line after lit-3's steps array closes
        in_lit3 = False

# Find the end of lit-3 lesson definition - look for }, after lit-3
for i, line in enumerate(lines):
    if "id: 'lit-3'" in line:
        # lit-3 ends at the next }, (closing brace + comma)
        for j in range(i, min(i+80, len(lines))):
            if lines[j].strip() == '},' or lines[j].strip() == '}' :
                print(f'lit-3 ends at line {j+1}: {lines[j].rstrip()}')
                print(f'  Next line: {j+2}: {lines[j+1].rstrip() if j+1 < len(lines) else "EOF"}')
                print(f'  Line after: {j+3}: {lines[j+2].rstrip() if j+2 < len(lines) else "EOF"}')
                break
        break

# Find where ARTS_LESSONS ends (before SHARED_LESSONS)
for i, line in enumerate(lines):
    if "export const SHARED_LESSONS" in line:
        print(f'\\nSHARED_LESSONS starts at line {i+1}')
        # Work backwards to find ARTS_LESSONS closing
        for j in range(i-1, max(i-10, 0), -1):
            if lines[j].strip() == '];':
                print(f'ARTS_LESSONS ends at line {j+1}')
                print(f'  Line before: {j}: {lines[j-1].rstrip() if j > 0 else "START"}')
                break
        break
