#!/usr/bin/env python
"""Extract all lesson data from rebuild_coremaths_modules.py.

The rebuild script uses this pattern:
    steps = [ info_step(...), predict_step(...), ... ]
    MODULEX_LESSONS.append(make_lesson( id, title, ..., steps ))

We parse the file as text, extract the data, and generate clean Python code.
"""

import re, os

def unescape_ts(s):
    """Unescape a TypeScript/Python string (\\' -> ', \\n -> \n, \\\\ -> \\)"""
    s = s.replace("\\\\", "\x00")  # temp marker
    s = s.replace("\\'", "'")
    s = s.replace('\\"', '"')
    s = s.replace("\\n", "\n")
    s = s.replace("\x00", "\\")
    return s

def extract_string(src, start):
    """Extract a single-quoted or double-quoted string from src starting at position start.
    Returns (content, end_pos) or (None, start) on failure."""
    if start >= len(src):
        return None, start
    q = src[start]
    if q not in ["'", '"']:
        return None, start
    i = start + 1
    while i < len(src):
        if src[i] == '\\' and i + 1 < len(src):
            i += 2
            continue
        if src[i] == q:
            raw = src[start+1:i]
            return raw, i + 1
        i += 1
    return None, len(src)

def extract_until(src, start, chars):
    """Skip whitespace and check if next char is in chars. Return position or -1."""
    i = start
    while i < len(src) and src[i] in ' \t\n\r':
        i += 1
    if i < len(src) and src[i] in chars:
        return i
    return -1

def find_matching_close(src, start, open_c, close_c):
    """Find matching closing bracket/paren from start (which should be at open_c)."""
    if start >= len(src) or src[start] != open_c:
        return -1
    depth = 1
    i = start + 1
    while i < len(src) and depth > 0:
        ch = src[i]
        if ch == '\\' and i + 1 < len(src):
            i += 2
            continue
        if ch == "'" or ch == '"':
            # Skip string
            _, i = extract_string(src, i)
            continue
        if ch == open_c:
            depth += 1
        elif ch == close_c:
            depth -= 1
        i += 1
    return i if depth == 0 else -1

def split_args(text):
    """Split comma-separated arguments at the top level."""
    args = []
    depth_p = depth_b = depth_br = 0
    current = ""
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == '\\' and i + 1 < len(text):
            current += ch + text[i+1]
            i += 2
            continue
        if ch == "'" or ch == '"':
            s, nxt = extract_string(text, i)
            current += text[i:nxt]
            i = nxt
            continue
        if ch == '(':
            depth_p += 1
        elif ch == ')':
            depth_p -= 1
        elif ch == '[':
            depth_b += 1
        elif ch == ']':
            depth_b -= 1
        elif ch == '{':
            depth_br += 1
        elif ch == '}':
            depth_br -= 1
        if ch == ',' and depth_p == 0 and depth_b == 0 and depth_br == 0:
            args.append(current.strip())
            current = ""
            i += 1
            continue
        current += ch
        i += 1
    if current.strip():
        args.append(current.strip())
    return args

def extract_steps_from_list(text):
    """Extract step objects from a `steps = [...]` block.
    Each step is a function call like info_step(...) or predict_step(...).
    Returns list of dicts."""
    steps = []
    # Find the opening [
    bracket = text.find("[")
    if bracket < 0:
        return steps
    
    close = find_matching_close(text, bracket, "[", "]")
    if close < 0:
        return steps
    
    inner = text[bracket+1:close-1] if close > bracket + 1 else ""
    if not inner.strip():
        return steps
    
    # Split by top-level commas
    items = split_args(inner)
    
    for item in items:
        item = item.strip()
        if not item:
            continue
        
        step = {}
        
        # Determine step type from the function name
        if item.startswith("info_step("):
            step["type"] = "info"
            args = extract_function_args(item)
            if len(args) >= 2:
                step["id"] = strip_quotes(args[0])
                step["content"] = unescape_ts(strip_quotes(args[1]))
        
        elif item.startswith("predict_step("):
            step["type"] = "predict"
            args = extract_function_args(item)
            if len(args) >= 7:
                step["id"] = strip_quotes(args[0])
                step["content"] = unescape_ts(strip_quotes(args[1]))
                step["predict_pattern"] = unescape_ts(strip_quotes(args[2]))
                step["predict_question"] = unescape_ts(strip_quotes(args[3]))
                # args[4] is the options list
                step["options"] = parse_options_list(args[4])
                step["correctIndex"] = int(strip_quotes(args[5])) if "'" in args[5] else int(args[5])
                step["explanation"] = unescape_ts(strip_quotes(args[6]))
        
        elif item.startswith("question_step("):
            step["type"] = "question"
            args = extract_function_args(item)
            if len(args) >= 7:
                step["id"] = strip_quotes(args[0])
                step["content"] = unescape_ts(strip_quotes(args[1]))
                step["exercise_question"] = unescape_ts(strip_quotes(args[2]))
                step["options"] = parse_options_list(args[3])
                step["correctIndex"] = int(strip_quotes(args[4])) if "'" in args[4] else int(args[4])
                step["explanation"] = unescape_ts(strip_quotes(args[5]))
        
        elif item.startswith("checkpoint_step("):
            step["type"] = "checkpoint"
            args = extract_function_args(item)
            if len(args) >= 3:
                step["id"] = strip_quotes(args[0])
                step["checkpoint_title"] = unescape_ts(strip_quotes(args[1]))
                # Parse the questions list
                step["checkpoint_questions"] = parse_checkpoint_questions(args[2])
        
        if step and "id" in step:
            steps.append(step)
    
    return steps

def extract_function_args(text):
    """Extract arguments from a function call like foo(arg1, arg2, ...)."""
    paren = text.find("(")
    if paren < 0:
        return []
    close = find_matching_close(text, paren, "(", ")")
    if close < 0:
        return []
    inner = text[paren+1:close-1]
    return split_args(inner)

def strip_quotes(s):
    s = s.strip()
    if (s.startswith("'") and s.endswith("'")) or (s.startswith('"') and s.endswith('"')):
        return s[1:-1]
    return s

def parse_options_list(text):
    """Parse ['opt1', 'opt2', ...] into list of strings."""
    text = text.strip()
    if not text.startswith("["):
        return []
    close = find_matching_close(text, 0, "[", "]")
    if close < 0:
        return []
    inner = text[1:close-1]
    items = split_args(inner)
    result = []
    for item in items:
        item = item.strip()
        if item:
            result.append(unescape_ts(strip_quotes(item)))
    return result

def parse_checkpoint_questions(text):
    """Parse a list of checkpoint question dicts."""
    text = text.strip()
    if not text.startswith("["):
        # Try to find the bracket
        bracket = text.find("[")
        if bracket < 0:
            return []
        text = text[bracket:]
    
    close = find_matching_close(text, 0, "[", "]")
    if close < 0:
        return []
    inner = text[1:close-1]
    
    # Find each { ... } object
    questions = []
    i = 0
    while i < len(inner):
        brace = inner.find("{", i)
        if brace < 0:
            break
        close_b = find_matching_close(inner, brace, "{", "}")
        if close_b < 0:
            break
        obj_text = inner[brace:close_b]
        q = {}
        
        # Extract fields
        q_match = re.search(r"'question':\s*'((?:[^'\\]|\\.)*)'", obj_text)
        if q_match:
            q["question"] = unescape_ts(q_match.group(1))
        o_match = re.search(r"'options':\s*(\[[^\]]*\])", obj_text)
        if o_match:
            q["options"] = parse_options_list(o_match.group(1))
        c_match = re.search(r"'correct':\s*(\d+)", obj_text)
        if c_match:
            q["correctIndex"] = int(c_match.group(1))
        # Also check for correctIndex
        ci_match = re.search(r"'correctIndex':\s*(\d+)", obj_text)
        if ci_match:
            q["correctIndex"] = int(ci_match.group(1))
        e_match = re.search(r"'explanation':\s*'((?:[^'\\]|\\.)*)'", obj_text)
        if e_match:
            q["explanation"] = unescape_ts(e_match.group(1))
        
        if q:
            questions.append(q)
        i = close_b
    
    return questions

# ── Main extraction ───────────────────────────────────────────────────

with open("scripts/rebuild_coremaths_modules.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find all module sections
module_pattern = re.compile(r"^# ── Module (\d+):\s*(.+?) ─", re.MULTILINE)
main_match = re.search(r"^# ── Main ─", content, re.MULTILINE)
main_start = main_match.start() if main_match else len(content)

all_lessons = {}

for m in module_pattern.finditer(content):
    mod_num = int(m.group(1))
    mod_title = m.group(2).strip()
    mod_start = m.start()
    
    # Find end of this module (next module or main section)
    next_m = module_pattern.search(content, mod_start + 1)
    mod_end = next_m.start() if next_m else main_start
    
    mod_text = content[mod_start:mod_end]
    module_lessons = []
    
    # Find all `steps = [...]` blocks followed by `MODULE...append(make_lesson(...))`
    # Pattern: steps = [ ... ]  then  MODULE.append(make_lesson( ... ))
    steps_pattern = re.compile(r"steps\s*=\s*(\[.*?\])\s*\n\s*(?:MODULE\d+_LESSONS\.append\(make_lesson)", re.DOTALL)
    
    pos = 0
    while True:
        # Find steps = [
        steps_match = re.search(r"(?<!def )steps\s*=\s*\[", mod_text[pos:])
        if not steps_match:
            break
        
        steps_start = pos + steps_match.start()
        bracket_pos = steps_start + steps_match.end() - 1  # position of [
        
        # Find matching ]
        close_bracket = find_matching_close(mod_text, bracket_pos, "[", "]")
        if close_bracket < 0:
            pos = steps_start + 1
            continue
        
        # Extract steps list content
        steps_inner = mod_text[bracket_pos:close_bracket]
        
        # Now find the make_lesson call that follows (uses variable `steps`)
        after_steps = mod_text[close_bracket:]
        ml_match = re.search(r"MODULE\d+_LESSONS\.append\(make_lesson\(", after_steps)
        if not ml_match:
            pos = close_bracket
            continue
        
        ml_paren = close_bracket + ml_match.start() + len("MODULE\d+_LESSONS.append(make_lesson(")
        ml_paren_actual = after_steps.find("(", ml_match.start())
        if ml_paren_actual >= 0:
            ml_paren = close_bracket + ml_paren_actual
        
        # Find the original position of the opening paren of make_lesson
        ml_start_in_mod = after_steps.find("make_lesson(")
        if ml_start_in_mod < 0:
            pos = close_bracket
            continue
        
        # Find the actual opening paren after make_lesson
        paren_pos_relative = after_steps.find("(", ml_start_in_mod)
        if paren_pos_relative < 0:
            pos = close_bracket
            continue
        
        paren_pos = close_bracket + paren_pos_relative
        close_paren = find_matching_close(mod_text, paren_pos, "(", ")")
        if close_paren < 0:
            pos = close_bracket
            continue
        
        # Extract make_lesson args
        ml_args_text = mod_text[paren_pos+1:close_paren-1]
        ml_args = split_args(ml_args_text)
        
        if len(ml_args) >= 13:
            lesson_id = strip_quotes(ml_args[0])
            title = unescape_ts(strip_quotes(ml_args[1]))
            subject = strip_quotes(ml_args[2])
            icon = strip_quotes(ml_args[3])
            programme = strip_quotes(ml_args[4])
            
            # Parse difficulty, minutes, xp
            difficulty = int(ml_args[5])
            minutes = int(ml_args[6])
            xp = int(ml_args[7])
            unit_id = strip_quotes(ml_args[8])
            
            # Extract steps from the steps list
            steps = extract_steps_from_list(steps_inner)
            
            module_lessons.append({
                "id": lesson_id,
                "title": title,
                "subject": subject,
                "icon": icon,
                "programme": programme,
                "difficulty": difficulty,
                "minutes": minutes,
                "xp": xp,
                "unit_id": unit_id,
                "steps": steps,
            })
            
            print(f"  Module {mod_num}: Extracted lesson '{lesson_id}' - '{title}' ({len(steps)} steps)")
        
        pos = close_bracket + 1
    
    all_lessons[mod_num] = {"title": mod_title, "lessons": module_lessons}
    print(f"  Module {mod_num} total: {len(module_lessons)} lessons")

# ── Generate output code ──────────────────────────────────────────────

def repr_for(s):
    """Return Python repr of a string, handling Unicode safely."""
    return repr(s)

def gen_step_code(step):
    t = step.get("type", "info")
    sid = repr(step["id"])
    
    if t == "info":
        return f"    i({sid}, {repr(step.get('content', ''))})"
    
    elif t == "predict":
        return (f"    p({sid}, {repr(step.get('content', ''))}, "
                f"{repr(step.get('predict_pattern', ''))}, "
                f"{repr(step.get('predict_question', ''))}, "
                f"{repr(step.get('options', []))}, "
                f"{step.get('correctIndex', 0)}, "
                f"{repr(step.get('explanation', ''))})")
    
    elif t == "question":
        return (f"    q({sid}, {repr(step.get('content', ''))}, "
                f"{repr(step.get('exercise_question', ''))}, "
                f"{repr(step.get('options', []))}, "
                f"{step.get('correctIndex', 0)}, "
                f"{repr(step.get('explanation', ''))})")
    
    elif t == "checkpoint":
        qs = step.get("checkpoint_questions", [])
        qs_parts = []
        for q in qs:
            qs_parts.append(
                f'{{"question": {repr(q.get("question", ""))}, '
                f'"options": {repr(q.get("options", []))}, '
                f'"correctIndex": {q.get("correctIndex", 0)}, '
                f'"explanation": {repr(q.get("explanation", ""))}}}'
            )
        qs_str = ", ".join(qs_parts)
        return f"    c({sid}, {repr(step.get('checkpoint_title', ''))}, [{qs_str}])"
    
    return ""

# Generate the complete Python file
lines = []
lines.append("""#!/usr/bin/env python
# ══════════════════════════════════════════════════════════════════════════
#  COMPLETE CORE MATHS — All 9 Modules × 5 Topics = 45 Lessons
#  Generated from rebuild_coremaths_modules.py
# ══════════════════════════════════════════════════════════════════════════

ALL_LESSONS = []
""")

for mod_num in sorted(all_lessons.keys()):
    mod = all_lessons[mod_num]
    lines.append(f"\n# ── Module {mod_num}: {mod['title']} ──\n")
    
    for lesson in mod["lessons"]:
        steps_code = ",\n".join(gen_step_code(s) for s in lesson["steps"])
        
        # Determine prereqs
        lid = lesson["id"]
        # First lesson of each module (except module 1) depends on last lesson of previous module
        is_first_in_module = True
        for other in mod["lessons"]:
            if other["id"] < lid:
                is_first_in_module = False
                break
        
        if is_first_in_module and mod_num > 1:
            prev_mod = all_lessons[mod_num - 1]
            if prev_mod["lessons"]:
                prereqs = [prev_mod["lessons"][-1]["id"]]
            else:
                prereqs = []
        elif not is_first_in_module:
            # Find the previous lesson in this module
            prev_id = None
            for other in mod["lessons"]:
                if other["id"] < lid:
                    prev_id = other["id"]
            prereqs = [prev_id] if prev_id else []
        else:
            prereqs = []
        
        shs = ["SHS 1"] if lesson["difficulty"] == 1 else (["SHS 2"] if lesson["difficulty"] == 2 else ["SHS 2", "SHS 3"])
        suggested = "SHS 1" if lesson["difficulty"] == 1 else ("SHS 2" if lesson["difficulty"] == 2 else "SHS 3")
        
        lines.append(f"""
ALL_LESSONS.append(L({repr(lesson['id'])}, {repr(lesson['title'])},
    {repr(lesson['subject'])}, {repr(lesson['icon'])}, {repr(lesson['programme'])},
    {lesson['difficulty']}, {lesson['minutes']}, {lesson['xp']},
    {repr(lesson['unit_id'])}, {repr(prereqs)}, {repr(shs)}, {repr(suggested)}, [
{steps_code},
]))""")
    
    lines.append(f"\n# End of Module {mod_num}\n")

total = sum(len(mod["lessons"]) for mod in all_lessons.values())
print(f"\n✅ Generated {total} lesson definitions total")

# Write the output
with open("scripts/generated_lessons.py", "w", encoding="utf-8") as f:
    f.write("".join(lines))

print(f"✅ Written to scripts/generated_lessons.py")
