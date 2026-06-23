import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('app/lib/learningContent.ts', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# ── 1. Find the ARTS_LESSONS closing ;;
arts_lessons_close = None
for i in range(len(lines)-1, -1, -1):
    if 'export const SHARED_LESSONS' in lines[i]:
        # ARTS_LESSONS should close a few lines above
        # The original file has:
        #   },   <- end of crs-2
        # ];    <- close ARTS_LESSONS
        # (blank)
        # comments
        # export const SHARED_LESSONS
        for j in range(i-1, max(0, i-10), -1):
            if lines[j].strip() == '];' and lines[j-1].strip().endswith('},'):
                arts_lessons_close = j
                print(f'ARTS_LESSONS closing at line {j+1}')
                for k in range(j-2, j+3):
                    print(f'  {k+1}: {lines[k].rstrip()}')
                break
        break

if arts_lessons_close is None:
    print('ERROR: Could not find ARTS_LESSONS closing')
    sys.exit(1)

# ── 2. Find the wrongly inserted lit-4, lit-5, lit-6 inside SHARED_UNITS
# lit-4 has 'id: "lit-4"' - look for all lit lesson objects between SHARED_UNITS and ARTS_LESSONS close
shared_units_line = None
for i, line in enumerate(lines):
    if 'export const SHARED_UNITS' in line:
        shared_units_line = i
        break

if shared_units_line:
    print(f'\nSHARED_UNITS at line {shared_units_line + 1}')
    # Find the line where lit-4 starts (after SHARED_UNITS definition)
    # In the current file, lit-4, lit-5, lit-6 are inside SHARED_UNITS
    lit4_start = None
    for i in range(shared_units_line, arts_lessons_close):
        line_stripped = lines[i].strip()
        if line_stripped == "'lit-4'" or 'id: ' in line_stripped and "'lit-4'" in line_stripped:
            lit4_start = i
            break
    
    if lit4_start is None:
        # Try looking for the lesson object directly
        for i in range(shared_units_line, arts_lessons_close):
            if "id: 'lit-4'" in lines[i]:
                lit4_start = i
                break
    
    if lit4_start:
        print(f'lit-4 starts at line {lit4_start + 1}: {lines[lit4_start].rstrip()[:80]}')
        # Find where lit-6 ends (the `  },` after lit-6)
        lit6_found = False
        lit6_end = None
        for i in range(lit4_start, arts_lessons_close):
            if "id: 'lit-6'" in lines[i]:
                lit6_found = True
            if lit6_found and lines[i].strip() == '],':
                # This is the closing of lit-6's steps array
                pass
            if lit6_found and lines[i].strip() == '},':
                # This closes lit-6 lesson object
                # BUT could also be closing a sub-object. Let's check if the next line is `];`
                if i + 1 < len(lines) and lines[i+1].strip() == '];':
                    lit6_end = i  # The }, before ];
                    print(f'lit-6 lesson ends at line {i+1} (followed by ];)')
                    break
                # Or the next relevant non-blank line
    
    if lit4_start is None or lit6_end is None:
        print(f'ERROR: Could not find lit-4 start or lit-6 end')
        print(f'lit4_start: {lit4_start}, lit6_end: {lit6_end}')
        # Print a range around where they should be
        for i in range(shared_units_line + 5, min(shared_units_line + 15, len(lines))):
            print(f'  {i+1}: {lines[i].rstrip()[:80]}')
        sys.exit(1)
    
    # ── 3. Extract the lit-4/5/6 content ──
    lit_lessons = lines[lit4_start:lit6_end + 1]  # Includes the `  },` closing lit-6
    
    print(f'\nExtracted {len(lit_lessons)} lines for lit-4, lit-5, lit-6')
    print(f'  First: {lit_lessons[0].rstrip()[:60]}')
    print(f'  Last:  {lit_lessons[-1].rstrip()[:60]}')
    
    # ── 4. Remove lit-4/5/6 from their current position ──
    # Also need to find and remove any orphaned ];
    # The lit_lessons includes the }, at the end. After that there might be:
    # ]; (if the script appended it)
    # ]; (original SHARED_UNITS closing)
    
    # Check what's right after lit6_end
    print(f'\nAfter lit-6 end (line {lit6_end+1}):')
    for k in range(lit6_end + 1, min(lit6_end + 6, len(lines))):
        print(f'  {k+1}: {lines[k].rstrip()}')
    
    # Check what's right AFTER the SHARED_UNITS definition
    # We need to find the original SHARED_UNITS closing
    
    # Remove lines from lit4_start to lit6_end (inclusive)
    del lines[lit4_start:lit6_end + 1]
    
    print(f'\nRemoved {lit6_end - lit4_start + 1} lines from position {lit4_start+1}-{lit6_end+1}')
    
    # After removal, recalculate arts_lessons_close position
    # (it shifted by -removed_count)
    removed_count = lit6_end - lit4_start + 1
    new_arts_close = arts_lessons_close - removed_count
    
    # ── 5. Close SHARED_UNITS properly ──
    # The lit_lessons were removed from inside SHARED_UNITS
    # Now we need to close SHARED_UNITS where they were
    # Find what's currently at the position after removal
    print(f'\nAt removal position (now line {lit4_start+1}):')
    for k in range(max(0, lit4_start-1), min(lit4_start+5, len(lines))):
        print(f'  {k+1}: {lines[k].rstrip()}')
    
    # Insert `];` to close SHARED_UNITS
    # The line at lit4_start might be blank, so insert after any blank
    insert_pos = lit4_start
    lines.insert(insert_pos, '];\n')
    print(f'Inserted SHARED_UNITS closing at line {insert_pos+1}')
    
    # Adjust new_arts_close since we inserted a line
    new_arts_close += 1
    
    # ── 6. Insert lit-4/5/6 before ARTS_LESSONS closing ──
    # First remove the trailing `},` that was the original closing of the last ARTS lesson
    # (line new_arts_close - 1 should be `},`)
    # But wait, we need to see the structure before arts_lessons_close
    
    print(f'\nBefore insertion at new ARTS_CLOSE (line {new_arts_close+1}):')
    for k in range(new_arts_close-3, new_arts_close+3):
        if 0 <= k < len(lines):
            print(f'  {k+1}: {lines[k].rstrip()}')
    
    # Insert lit_lessons before the `];` at new_arts_close
    lines[new_arts_close:new_arts_close] = lit_lessons
    
    print(f'Inserted lit-4/5/6 ({len(lit_lessons)} lines) at line {new_arts_close+1}')
    
    # ── 7. Verify no duplicate `];` ──
    # Check for consecutive `];`
    for i in range(len(lines)-1):
        if lines[i].strip() == '];' and lines[i+1].strip() == '];':
            print(f'WARNING: Duplicate ]; at lines {i+1} and {i+2}')
            del lines[i+1]
            print('  Removed duplicate')
            break
    
    # ── 8. Write the file ──
    with open('app/lib/learningContent.ts', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print('\n✅ All fixes applied!')
