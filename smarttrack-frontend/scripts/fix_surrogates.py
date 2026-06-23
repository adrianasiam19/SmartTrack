import sys

with open("scripts/generate_coremaths.py", "r", encoding="utf-8", errors="surrogateescape") as f:
    content = f.read()

slash_u = "\\U"

surrogate_locations = []
for i, ch in enumerate(content):
    cp = ord(ch)
    if 0xD800 <= cp <= 0xDFFF:
        surrogate_locations.append((i, cp))

print(f"Found {len(surrogate_locations)} surrogate characters")

pairs = []
i = 0
while i < len(surrogate_locations):
    pos, cp = surrogate_locations[i]
    if 0xD800 <= cp <= 0xDBFF:
        if i + 1 < len(surrogate_locations):
            next_pos, next_cp = surrogate_locations[i + 1]
            if 0xDC00 <= next_cp <= 0xDFFF and next_pos == pos + 1:
                full_cp = 0x10000 + (cp - 0xD800) * 0x400 + (next_cp - 0xDC00)
                pairs.append((pos, next_pos + 1, full_cp))
                i += 2
                continue
        print(f"  Orphan high surrogate at position {pos}: U+{cp:04X}")
    elif 0xDC00 <= cp <= 0xDFFF:
        print(f"  Orphan low surrogate at position {pos}: U+{cp:04X}")
    i += 1

print(f"Found {len(pairs)} surrogate pairs")

new_content = []
last_end = 0
for start, end, full_cp in pairs:
    new_content.append(content[last_end:start])
    new_content.append(chr(full_cp))
    last_end = end
    ch = chr(full_cp)
    print(f"  Position {start}: surrogate pair -> U+{full_cp:04X} '{ch}'")

new_content.append(content[last_end:])
result = "".join(new_content)

for i, ch in enumerate(result):
    cp = ord(ch)
    if 0xD800 <= cp <= 0xDFFF:
        print(f"ERROR: Surrogate still remaining at position {i}")
        sys.exit(1)

with open("scripts/generate_coremaths.py", "w", encoding="utf-8") as f:
    f.write(result)

print(f"Fixed! Replaced {len(pairs)} surrogate pairs.")

try:
    compile(result, "scripts/generate_coremaths.py", "exec")
    print("Syntax check: OK")
except SyntaxError as e:
    print(f"Syntax error after fix: {e}")
