#!/usr/bin/env python
"""Fix js_str() to escape newlines and use single-quoted strings."""

with open('scripts/generate_all_coremaths.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# js_str() starts at line 7 (index 6) and ends at line 11 (index 10)
# Replace with single-quoted version that escapes newlines
new_js_str = [
    'def js_str(s: str) -> str:\n',
    '    """Escape for TypeScript (single quotes, newlines as \\n)."""\n',
    '    escaped = (s\n',
    '        .replace("\\\\", "\\\\\\\\")\n',
    "        .replace(\"'\", \"\\\\'\")\n",
    '        .replace("\\n", "\\\\n")\n',
    '    )\n',
    "    return \"'\" + escaped + \"'\"\n",
    '\n',
]

lines[6:11] = new_js_str

with open('scripts/generate_all_coremaths.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('SUCCESS: js_str() replaced with single-quoted version')
