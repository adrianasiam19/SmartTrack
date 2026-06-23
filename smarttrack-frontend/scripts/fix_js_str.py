#!/usr/bin/env python
"""Fix js_str() in generate_all_coremaths.py to use backtick template literals."""

with open('scripts/generate_all_coremaths.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = """def js_str(s: str) -> str:
    \"\"\"Escape a string for TypeScript single-quote literal.\"\"\"
    escaped = s.replace("\\\\", "\\\\\\\\").replace("'", "\\\\'")
    return f"'{escaped}'\""""

new = """def js_str(s: str) -> str:
    \"\"\"Escape a string for a TypeScript backtick template literal.\"\"\"
    escaped = s.replace("\\\\", "\\\\\\\\").replace("\`", "\\\\\`").replace("${", "\\\\${")
    return f"\`{escaped}\`\""""

if old in content:
    content = content.replace(old, new)
    with open('scripts/generate_all_coremaths.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('SUCCESS: js_str() updated to use backtick template literals')
else:
    print('FAILED: Could not find old js_str() in file')
    # Debug
    idx = content.find('def js_str')
    if idx >= 0:
        print('Found at index', idx)
        print(repr(content[idx:idx+250]))
