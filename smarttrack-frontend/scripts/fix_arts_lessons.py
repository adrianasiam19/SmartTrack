import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('app/lib/learningContent.ts', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. Check for orphaned `];` around ARTS_LESSONS closing
# Find SHARED_LESSONS
for i, line in enumerate(lines):
    if 'export const SHARED_LESSONS' in line:
        print(f'SHARED_LESSONS at line {i+1}')
        # Print the 5 lines before it
        for j in range(max(0, i-6), i):
            print(f'  {j+1}: {lines[j].rstrip()}')
        break

# 2. Check for any other syntax issues - find line 1852 error area
print(f'\n--- Lines around 1850-1860 ---')
for i in range(1849, min(1861, len(lines))):
    print(f'{i+1}: {lines[i].rstrip()[:120]}')
