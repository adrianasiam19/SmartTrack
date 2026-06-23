import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('app/lib/learningContent.ts', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# ── 1. Find ARTS_LESSONS closing ;; at line 2117 ──
arts_close = None
for i, line in enumerate(lines):
    # Look for `];` that closes ARTS_LESSONS - before SHARED_UNITS
    if 'export const SHARED_UNITS' in line:
        # Walk backwards to find the `];` that closes ARTS_LESSONS
        for j in range(i-1, max(0, i-10), -1):
            stripped = lines[j].strip()
            if stripped == '];':
                arts_close = j
                print(f'ARTS_LESSONS closing at line {j+1}')
                for k in range(j-2, j+3):
                    print(f'  {k+1}: {lines[k].rstrip()}')
                break
        break

if arts_close is None:
    print('ERROR: Could not find ARTS_LESSONS closing')
    sys.exit(1)

# ── 2. Find lit-4/5/6 (outside any array, between SHARED_UNITS and ARTS_LESSONS orphan) ──
lit4_start = None
lit6_end = None

for i, line in enumerate(lines):
    if "id: 'lit-4'" in line:
        lit4_start = i
        print(f'lit-4 starts at line {i+1}')
        break

if lit4_start is None:
    print('ERROR: Could not find lit-4')
    sys.exit(1)

# Find the end of the lit-6 lesson - it's the `},` before the orphaned `];`
# Walk forward from lit-4 start to find the last lit-6 line
# Lines 2144 to about 2400 contain lit-4/5/6 + orphaned `];`
# Find the last `},` before the orphaned `];`
orphan_close = None
for i in range(lit4_start, len(lines)):
    if lines[i].strip() == '];' and 'SHARED_UNITS' not in lines[i-10] if i >= 10 else True:
        # This might be the orphaned `];` or ARTS_LESSONS closing
        # Check if the content between lit4_start and here has lit-6
        orphan_close = i
        break

if orphan_close is None:
    print('ERROR: Could not find closing after lit-4')
    sys.exit(1)

# The lit lessons end before the orphan `];`
# lit6_end is the `},` before orphan `];`
lit6_end = orphan_close - 1
# But skip blank lines
while lit6_end > lit4_start and lines[lit6_end].strip() == '':
    lit6_end -= 1

print(f'lit-4/5/6 content from line {lit4_start+1} to {lit6_end+1}')
print(f'  First: {lines[lit4_start].rstrip()[:60]}')
print(f'  Last: {lines[lit6_end].rstrip()[:60]}')

# Verify the last line is `},` or similar
print(f'  Last line check: {lines[lit6_end].rstrip()}')
print(f'  Orphan ]; at line {orphan_close+1}: {lines[orphan_close].rstrip()}')

# ── 3. Extract lit-4/5/6 content ──
lit_lessons = lines[lit4_start:lit6_end + 1]

# ── 4. Remove lit-4/5/6 AND orphaned `];` from current position ──
del lines[lit4_start:orphan_close + 1]
print(f'\nRemoved {orphan_close - lit4_start + 1} lines (lit lessons + orphan ])')

# Adjust arts_close position if it's after the removal point
if arts_close >= lit4_start:
    # arts_close is before lit4_start, so no adjustment needed
    pass

# ── 5. Insert lit-4/5/6 before ARTS_LESSONS closing ──
# Insert at arts_close position (before `];`)
lines[arts_close:arts_close] = lit_lessons

print(f'Inserted {len(lit_lessons)} lines of lit-4/5/6 at line {arts_close+1} (before ARTS_LESSONS `];`)')

# Verify the structure
print(f'\nVerification - lines around insertion:')
for k in range(arts_close-1, min(arts_close+5, len(lines))):
    print(f'  {k+1}: {lines[k].rstrip()[:80]}')

# ── 6. Check for duplicate `];` ──
for i in range(len(lines)-1):
    if lines[i].strip() == '];' and lines[i+1].strip() == '];':
        print(f'WARNING: Duplicate ]; at lines {i+1} and {i+2}')
        # Keep the first one (which is probably the ARTS_LESSONS close)
        # Remove the second one (which was inserted by previous script)
        del lines[i+1]
        print('  Removed duplicate')

# ── 7. Write file ──
with open('app/lib/learningContent.ts', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('\n✅ All fixes applied!')
