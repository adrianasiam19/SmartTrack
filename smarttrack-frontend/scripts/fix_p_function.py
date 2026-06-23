#!/usr/bin/env python
"""Fix the p() function to handle both 6-arg (appended) and 7-arg (original) call patterns."""

with open("scripts/generate_coremaths.py", "r", encoding="utf-8") as f:
    content = f.read()

# First, revert any previous broken changes to the p() definition
# Find and replace the broken p() function with a flexible *args version
old_func = """def p(sid, content, pattern, question=None, options, correct, explanation):
    return {"id": sid, "type": "predict", "content": content,
            "predict": {"pattern": pattern, "question": question or "",
                        "options": options, "correctIndex": correct,
                        "explanation": explanation}}"""

new_func = """def p(sid, content, pattern, *args):
    if len(args) == 4:
        question, options, correct, explanation = args
    elif len(args) == 3:
        question, options, correct, explanation = "", args[0], args[1], args[2]
    else:
        raise ValueError("p() expects 6 or 7 arguments, got " + str(3 + len(args)))
    return {"id": sid, "type": "predict", "content": content,
            "predict": {"pattern": pattern, "question": question,
                        "options": options, "correctIndex": correct,
                        "explanation": explanation}}"""

if old_func in content:
    content = content.replace(old_func, new_func, 1)
    with open("scripts/generate_coremaths.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("SUCCESS: Replaced p() function with flexible *args version")
else:
    print("ERROR: Could not find p() function definition. Searching...")
    for i, line in enumerate(content.split("\n")):
        if "def p(" in line:
            print(f"  Line {i+1}: {line}")
            for j in range(i, min(i+6, len(content.split("\n")))):
                print(f"    {j+1}: {content.split(chr(10))[j][:200]}")
            break

# Verify syntax
import ast
try:
    ast.parse(content)
    print("SYNTAX CHECK: No syntax errors!")
except SyntaxError as e:
    print(f"SYNTAX ERROR at line {e.lineno}: {e.msg}")
