#!/usr/bin/env python
"""Fix js_str() to escape newlines and use single-quoted strings instead of backtick template literals."""

BT = chr(96)  # backtick

with open('scripts/generate_all_coremaths.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = (
    'def js_str(s: str) -> str:\n'
    '    """Escape a string for a TypeScript backtick template literal."""\n'
    '    escaped = s.replace("\\\\", "\\\\\\\\").replace("' + BT + '", "\\\\' + BT + '").replace("${", "\\\\${")\n'
    '    return f"' + BT + '{escaped}' + BT + '"\n'
)

new = (
    'def js_str(s: str) -> str:\n'
    '    """Escape for a TypeScript single-quote literal (newlines become \\\\n)."""\n'
    '    escaped = (s\n'
    '        .replace("\\\\", "\\\\\\\\")\n'
    '        .replace("\'", "\\\\\'")\n'
    '        .replace("\\n", "\\\\n")\n'
    '    )\n'
    '    return "\'" + escaped + "\'"\n'
)

if old in content:
    content = content.replace(old, new)
    with open('scripts/generate_all_coremaths.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('SUCCESS: js_str() updated')
else:
    print('FAILED: Could not find old js_str()')
    idx = content.find('def js_str')
    if idx >= 0:
        print('Current js_str():')
        print(content[idx:idx+200])
