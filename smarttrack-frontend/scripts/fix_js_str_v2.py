#!/usr/bin/env python
"""Fix js_str() in generate_all_coremaths.py to use single-quoted strings with escaped newlines."""

with open('scripts/generate_all_coremaths.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''def js_str(s: str) -> str:
    """Escape a string for a TypeScript backtick template literal."""
    escaped = s.replace("\\\\", "\\\\\\\\").replace("\`", "\\\\\`").replace("${", "\\\\${")
    return f"\`{escaped}\`\""""

new = '''def js_str(s: str) -> str:
    """Escape a string for a TypeScript single-quote literal.
    Uses \\n for newlines so multi-line content stays valid TypeScript.
    """
    escaped = (s
        .replace("\\\\", "\\\\\\\\")
        .replace("'", "\\\\'")
        .replace("\\n", "\\\\n")
    )
    return f"'{escaped}'\""""

if old in content:
    content = content.replace(old, new)
    with open('scripts/generate_all_coremaths.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('SUCCESS: js_str() updated to use single-quoted \\n-escaped strings')
else:
    print('FAILED: Could not find old js_str()')
    idx = content.find('def js_str')
    if idx >= 0:
        print('Current js_str:')
        print(content[idx:idx+300])
