import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('app/lib/learningContent.ts', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the literature unit definition
for i, line in enumerate(lines):
    if "id: 'literature'" in line:
        print(f'Literature unit at line {i+1}')
        for j in range(i, min(i+12, len(lines))):
            print(f'  {j+1}: {lines[j].rstrip()}')
        break
