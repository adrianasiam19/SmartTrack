"""Add surrogate sanitization before writing to file in generate_coremaths.py.

Replace instances of f.write(content) with code that sanitizes surrogates first.
"""

with open("scripts/generate_coremaths.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find all f.write(new_content) and f.write(full_content) calls
# Replace them with sanitized versions
import re

# Add a helper function after the make_lesson function
# Find the end of format_steps function (just before define_lessons)
helper_func = '''
def sanitize_surrogates(s: str) -> str:
    """Replace surrogate pairs with proper Unicode characters."""
    result = []
    i = 0
    while i < len(s):
        cp = ord(s[i])
        if 0xD800 <= cp <= 0xDBFF:  # High surrogate
            if i + 1 < len(s):
                next_cp = ord(s[i + 1])
                if 0xDC00 <= next_cp <= 0xDFFF:  # Low surrogate
                    full = 0x10000 + (cp - 0xD800) * 0x400 + (next_cp - 0xDC00)
                    result.append(chr(full))
                    i += 2
                    continue
        elif 0xDC00 <= cp <= 0xDFFF:  # Orphan low surrogate
            i += 1
            continue
        result.append(s[i])
        i += 1
    return "".join(result)


'''

# Insert the helper function before define_lessons
# Find where define_lessons starts
insert_pos = content.find("\ndef define_lessons")
if insert_pos >= 0:
    content = content[:insert_pos] + helper_func + content[insert_pos:]
    print(f"Inserted sanitize_surrogates function at position {insert_pos}")
else:
    print("WARNING: Could not find define_lessons function")

# Now replace all f.write calls to use sanitize
# Pattern 1: f.write(new_content)
new_content_old = "        with open(filepath, \"w\", encoding=\"utf-8\") as f:\n            f.write(new_content)"
new_content_new = "        with open(filepath, \"w\", encoding=\"utf-8\") as f:\n            sanitized = sanitize_surrogates(new_content)\n            f.write(sanitized)"

if new_content_old in content:
    content = content.replace(new_content_old, new_content_new)
    print("Fixed f.write(new_content)")
else:
    print("WARNING: Could not find f.write(new_content) pattern")

# Pattern 2: f.write(full_content)
full_content_old = "        with open(filepath, \"w\", encoding=\"utf-8\") as f:\n            f.write(full_content)"
full_content_new = "        with open(filepath, \"w\", encoding=\"utf-8\") as f:\n            sanitized = sanitize_surrogates(full_content)\n            f.write(sanitized)"

if full_content_old in content:
    content = content.replace(full_content_old, full_content_new)
    print("Fixed f.write(full_content)")
else:
    print("WARNING: Could not find f.write(full_content) pattern")

# Write back
with open("scripts/generate_coremaths.py", "w", encoding="utf-8") as f:
    f.write(content)

# Verify syntax
try:
    compile(content, "scripts/generate_coremaths.py", "exec")
    print("Syntax check: OK")
except SyntaxError as e:
    print(f"Syntax error: {e}")
