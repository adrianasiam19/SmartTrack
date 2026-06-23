import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('app/lib/learningContent.ts', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# ── Fix 1: Remove the orphaned `];` at line 2401 (0-indexed: 2400) ──
# Before: there should be one ]; closing ARTS_LESSONS after the new lessons
# Let's find the extra one
for i in range(len(lines)-1, -1, -1):
    if lines[i].strip() == '];':
        # Check if the line before is also ];
        if i > 0 and lines[i-1].strip() == '];':
            print(f'Found duplicate ]; at line {i+1}, removing it')
            del lines[i]
            break
        elif i > 1 and lines[i-2].strip() == '];':
            print(f'Found duplicate ]; at line {i-1}')
            del lines[i-1]
            break

# ── Fix 2: Fix the unterminated string literal in lit-3-s6's explanation ──
# The issue is: '...characters don't...' — the apostrophe in "don't" breaks the single-quoted TS string
# Find the line with "don't" in a single-quoted TS string context
for i, line in enumerate(lines):
    if "don't" in line and "explanation" in line or "content" in line and "don't" in line:
        # Check if the line uses single quotes for the string
        stripped = line.lstrip()
        if stripped.startswith("'") or stripped.startswith("\"'"):
            print(f'Found potential issue at line {i+1}: {line.rstrip()[:100]}')

# Search for the problematic string
# The explanation is: 'An **aside** is when...don't...'
# We need to change it from single-quoted to double-quoted or escape the apostrophe
for i, line in enumerate(lines):
    if "don\\'t" in line:
        print(f'Line {i+1} already has escaped apostrophe: {line.rstrip()[:80]}')
    elif "don't" in line:
        # Check context - is this in a single-quoted string?
        # Look for "don't" that might break a single-quoted TS string
        # The lit-3-s6 explanation starts with 'An **aside** is...
        if "aside" in line and "don't" in line:
            print(f'Found unescaped apostrophe at line {i+1}: {line.rstrip()[:100]}')
            # Fix: change the opening quote from ' to " and closing from ' to "
            # But first check if it's single-quoted
            stripped = line.lstrip()
            if stripped.startswith("'"):
                # Replace the opening ' with "
                indent = line[:len(line) - len(stripped)]
                rest = stripped[1:]
                # Find where this string ends - it ends with ',
                # But that might be hard to find. Let's just replace don't with don\\'t
                lines[i] = line.replace("don't", "don\\'t")
                print(f'  Fixed: escaped apostrophe in "don\'t"')
                break

# Also search for other potential issues - look for unescaped apostrophes in single-quoted strings in lit-3-s6
# Actually let me just find the exact line and fix it properly
# The line should be like: 'An **aside** is when a character speaks... **Dramatic irony** is when the audience knows something characters don't. WASSCE...'
# Let's find it by looking for lines with "aside" AND "don't"

with open('app/lib/learningContent.ts', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('\n✅ Fixes applied')
