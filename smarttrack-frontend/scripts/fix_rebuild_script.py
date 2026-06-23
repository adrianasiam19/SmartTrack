#!/usr/bin/env python
"""Fix apostrophe escaping in rebuild_coremaths_modules.py"""

BACKSLASH = b'\x5c'
QUOTE = b'\x27'

with open('scripts/rebuild_coremaths_modules.py', 'rb') as f:
    data = bytearray(f.read())

# Pattern: two backslashes followed by quote: \\ + '
# Fix: add one more backslash: \\ + \ + '
# In bytes: \x5c \x5c \x27 -> \x5c \x5c \x5c \x27

count = 0
i = 0
while i < len(data) - 2:
    if data[i] == BACKSLASH[0] and data[i+1] == BACKSLASH[0] and data[i+2] == QUOTE[0]:
        # Insert an extra backslash before the quote
        data.insert(i+2, BACKSLASH[0])
        count += 1
        i += 4  # Skip past the fixed sequence
    else:
        i += 1

with open('scripts/rebuild_coremaths_modules.py', 'wb') as f:
    f.write(data)

print(f"Fixed {count} apostrophe escape sequences")

# Verify syntax
import ast
try:
    with open('scripts/rebuild_coremaths_modules.py', 'r', encoding='utf-8') as f:
        content = f.read()
    ast.parse(content)
    print("No syntax errors!")
except SyntaxError as e:
    print(f"Error at line {e.lineno}: {e.msg}")
    lines = content.split('\n')
    if e.lineno and e.lineno <= len(lines):
        print(f"  Line: {repr(lines[e.lineno-1][:200])}")
