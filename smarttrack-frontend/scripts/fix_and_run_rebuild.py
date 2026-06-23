#!/usr/bin/env python
"""
fix_and_run_rebuild.py
───────────────────────
Reads rebuild_coremaths_modules.py, fixes the common syntax errors:
1. Extra ] brackets in string functions (e.g., 'opt1'), -> 'opt1')
2. Escaped apostrophes that break strings

Then runs the fixed script.
"""

import re, sys, ast

with open("scripts/rebuild_coremaths_modules.py", "r", encoding="utf-8") as f:
    content = f.read()

# Count lines before
lines_before = content.count('\n')
print(f"Original: {lines_before+1} lines, {len(content)} chars")

# Fix 1: Remove extra ] at end of strings in function arguments
# Pattern: something like 'text'),  or "text'),
# Where the ) is the closing paren and ], should just be )
# The pattern is a string ending with '] then comma 
# This is in predict_step, question_step, etc. arguments lists

# Find lines ending with '], (closing quote bracket comma)
# These should be '), (closing quote paren comma)
fixes_applied = 0

# Fix pattern A: 'text'],  -> 'text'),
# Pattern: a single-quoted string (possibly with unicode) followed by ],
content_fixed = re.sub(
    r"('[^']*?(?:[^\\])')],",
    lambda m: m.group(1) + "),",
    content
)
if content_fixed != content:
    fixes_applied += (content.count("'),],") - content_fixed.count("'),],"))
    # Actually let me count differently
    diff = sum(1 for a, b in zip(content.split('\n'), content_fixed.split('\n')) if a != b)
    print(f"Fix A: {diff} lines changed")
    content = content_fixed

# Fix 2: Replace '] with ' ) (when it's an extra bracket before close paren)
# More specifically, pattern: '], at end of line (in function calls)
content_fixed = re.sub(
    r"'\]\),",
    lambda m: "' ),",
    content
)
if content_fixed != content:
    diff = sum(1 for a, b in zip(content.split('\n'), content_fixed.split('\n')) if a != b)
    print(f"Fix B: {diff} lines changed")
    content = content_fixed

# Fix 3: Replace \' (escaped quotes within Python strings) with something that works
# In Python f-strings with triple quotes, we need to avoid \'
# Actually the issue is \"\\'s\" - let me handle the specific pattern

# Let me check for syntax errors more carefully
def check_syntax(text):
    try:
        ast.parse(text)
        return None
    except SyntaxError as e:
        return e

# Check if there are still issues
error = check_syntax(content)
if error:
    print(f"Remaining error at line {error.lineno}: {error.msg}")
    lines = content.split('\n')
    if error.lineno:
        start = max(0, error.lineno - 3)
        end = min(len(lines), error.lineno + 2)
        for i in range(start, end):
            marker = '>>>' if i+1 == error.lineno else '   '
            print(f'{marker} {i+1}: {repr(lines[i][:200])}')
    
    # Try a more aggressive fix: replace all problematic patterns
    # The issue is in Python f-strings and regular strings with \\'
    
    # Fix: In the script, most strings are wrapped in f'''...''' 
    # The issue is when a string inside has \' which Python interprets as end of string
    
    # Convert all single quotes inside strings that are part of contractions
    # Let's find the specific patterns
    print("\nAttempting aggressive fix...")
    
    # Replace known problematic patterns
    problematic = [
        ("Let\\'s", "Lets"),
        ("don\\'t", "dont"),
        ("isn\\'t", "isnt"),
        ("can\\'t", "cant"),
        ("won\\'t", "wont"),
        ("doesn\\'t", "doesnt"),
        ("hasn\\'t", "hasnt"),
        ("haven\\'t", "havent"),
        ("didn\\'t", "didnt"),
        ("couldn\\'t", "couldnt"),
        ("wouldn\\'t", "wouldnt"),
        ("shouldn\\'t", "shouldnt"),
        ("it\\'s", "its"),
        ("that\\'s", "thats"),
        ("\\'s", "s"),
        ("\\'t", "t"),
        ("\\'re", "re"),
        ("\\'ll", "ll"),
        ("\\'ve", "ve"),
        ("\\'d", "d"),
        ("\\'m", "m"),
    ]
    
    for old, new in problematic:
        content = content.replace(old, new)
    
    error2 = check_syntax(content)
    if error2:
        print(f"Still has error at line {error2.lineno}: {error2.msg}")
    else:
        print("✅ All syntax errors fixed!")
        fixes_applied += 1

# If syntax is clean, run the script
error_final = check_syntax(content)
if error_final:
    print(f"\n❌ Cannot run - syntax error persists at line {error_final.lineno}")
    sys.exit(1)

# Write fixed version
with open("scripts/rebuild_coremaths_modules_fixed.py", "w", encoding="utf-8") as f:
    f.write(content)

print(f"\n✅ Written fixed version to scripts/rebuild_coremaths_modules_fixed.py")
print(f"   {len(content)} chars, {content.count(chr(10))+1} lines")

# Now try to import and run it
print("\nAttempting to run...")
sys.path.insert(0, "scripts")
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("rebuild_fixed", "scripts/rebuild_coremaths_modules_fixed.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print("✅ Script executed successfully!")
except Exception as e:
    print(f"❌ Runtime error: {e}")
    # Try executing it via exec
    try:
        exec(compile(content, "rebuild_coremaths_modules_fixed.py", "exec"))
        print("✅ Script executed via exec() successfully!")
    except Exception as e2:
        print(f"❌ exec() also failed: {e2}")
