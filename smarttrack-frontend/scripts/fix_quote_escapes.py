#!/usr/bin/env python
"""
fix_quote_escapes.py
────────────────────
Fixes Python source code in rebuild_coremaths_modules.py where
double-backslash-tick (\\') appears inside single-quoted strings.

In a Python single-quoted string, \\' is parsed as:
  \\ → escaped backslash = literal backslash
  ' → string terminator (ENDS THE STRING)

This breaks the string. The correct escape for a literal apostrophe
in a single-quoted string is \\' (backslash + tick), which needs to
be \\\\' in the Python source file (escaped backslash + escaped quote).

So we need to change \\' to \\\\' in the Python source file.
"""

import re

filepath = 'scripts/rebuild_coremaths_modules.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# The problem: In Python source code, \\' inside a '...' string means:
#   \\ = one literal backslash  
#   ' = END OF STRING
# The correct escape for apostrophe in '...' is: \\' which needs \\\\' in source
# But that's confusing to write. Let me use a different approach.

# The file currently has things like:
#   'Let\'s start'  — this is LITERALLY: 'Let\'s start' in source code
# In Python, this is parsed as:
#   'Let\' + (end of string)  ... BROKEN
# Because \\ is an escaped backslash, then ' ends the string.

# What we need: 'Let\\'s start' (three backslashes before the quote)
# But in the SOURCE FILE, we write: Let\\\'s
# Which Python parses as:
#   \\ = one literal backslash
#   \' = one literal quote (escaped)
#   s = s
# Result: Let\'s  ✓

# Actually wait. Let me think more carefully about the file byte content.

# If the file contains the bytes: Let\'s (L, e, t, \, ', s)
# Python reads: Let + \' (escaped quote = ') + s = Let's  ✓
# This is what we need!

# If the file contains the bytes: Let\\'s (L, e, t, \, \, ', s)
# Python reads: Let + \\ (escaped backslash = \) + ' (string terminator) = broken

# So we need to find places where the file has \\' (two backslashes + quote)
# and replace them with \' (one backslash + quote).

# Wait, hmm. Let me check what the ACTUAL bytes are in the file.

# From the earlier analysis via repr(), the file has:
# Let\\\\'s in repr output, meaning the raw file bytes are: Let\\'s (L,e,t,\,,\,',s)

# Wait no, repr of a string ALSO escapes backslashes. So repr output showing
# \\ means the actual character is a single backslash. And \\\\ means two backslashes.

# From the read_files output, I saw: Let\\'s
# In read_files, backslashes are displayed as-is. So the file has:
# L, e, t, \, \, ', s  = Let\\'s

# In Python, '...Let\\'s...' is parsed as:
# ' (start string)
# ...Let\
# ' (END STRING! because \\ = one literal backslash, then ' is the terminator)

# So the file currently has TWO backslashes before the apostrophe, making it:
# \\ = one backslash in Python string
# ' = string terminator

# The fix: change \\' to \' (one backslash) in the file.
# With one backslash: 'Let\'s' would be parsed as:
# ' (start string)
# Let
# \' = escaped quote = literal '
# s
# ' (end string)
# Result: Let's

# So I need to replace \\' with \' in the Python source.

# Count the pattern: two backslashes followed by a single quote
idx = 0
count = 0
fixed = 0
result = []

while idx < len(content):
    # Look for \\' pattern (backslash backslash quote)
    if idx + 2 < len(content) and content[idx] == '\\' and content[idx+1] == '\\' and content[idx+2] == "'":
        # Check if a letter follows (to confirm it's an apostrophe)
        if idx + 3 < len(content) and content[idx+3].isalpha():
            # This is likely a broken apostrophe like \\'s → should be \'s
            # Replace \\' with \' 
            result.append('\\' + "'")  # one backslash + quote
            idx += 3
            fixed += 1
            continue
        # Also handle \\' followed by non-alpha (like at end of word)
        # For safety, only handle \\' followed by letters
    result.append(content[idx])
    idx += 1

new_content = ''.join(result)

print(f"Fixed {fixed} apostrophe escape sequences")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

# Verify syntax
try:
    compile(new_content, filepath, 'exec')
    print("✅ No syntax errors!")
except SyntaxError as e:
    print(f"❌ Syntax error at line {e.lineno}: {e.msg}")
    lines = new_content.split('\n')
    if e.lineno and e.lineno <= len(lines):
        print(f"   Line content: {repr(lines[e.lineno-1][:200])}")
