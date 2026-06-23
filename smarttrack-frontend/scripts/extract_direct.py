#!/usr/bin/env python
"""Ultra-simple extraction - find make_lesson calls by looking backwards for steps."""

import re, os

def unescape(s):
    s = s.replace("\\\\", "\x00")
    s = s.replace("\\'", "'").replace('\\"', '"')
    s = s.replace("\\n", "\n")
    s = s.replace("\x00", "\\")
    return s

def find_paren_depth(text, start, open_c='(', close_c=')'):
    """Find matching closing paren from start position of open paren."""
    if text[start] != open_c:
        text.find(open_c, start)
    depth = 1
    i = start + 1
    in_str = False
    str_char = None
    while i < len(text) and depth > 0:
        ch = text[i]
        if ch == '\\':
            i += 2
            continue
        if ch == "'" or ch == '"':
            if not in_str:
                in_str = True
                str_char = ch
            elif ch == str_char:
                in_str = False
            i += 1
            continue
        if not in_str:
            if ch == open_c:
                depth += 1
            elif ch == close_c:
                depth -= 1
        i += 1
    return i if depth == 0 else -1

def split_top_level(text):
    """Split by commas at top level."""
    parts = []
    depth = 0
    current = ""
    in_str = False
    str_char = None
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == '\\':
            current += ch
            i += 1
            if i < len(text):
                current += text[i]
            i += 1
            continue
        if ch == "'" or ch == '"':
            if not in_str:
                in_str = True
                str_char = ch
            elif ch == str_char:
                in_str = False
            current += ch
            i += 1
            continue
        if not in_str:
            if ch in '([{':
                depth += 1
            elif ch in ')]}':
                depth -= 1
            elif ch == ',' and depth == 0:
                parts.append(current.strip())
                current = ""
                i += 1
                continue
        current += ch
        i += 1
    if current.strip():
        parts.append(current.strip())
    return parts

def extract_string(text, pos):
    """Extract a single or double quoted string at position pos."""
    if pos >= len(text):
        return None, pos
    q = text[pos]
    if q not in ["'", '"']:
        return None, pos
    i = pos + 1
    while i < len(text):
        if text[i] == '\\':
            i += 2
            continue
        if text[i] == q:
            return text[pos+1:i], i + 1
        i += 1
    return None, len(text)

def get_str_arg(args, idx):
    """Get a string argument from args list, stripping quotes."""
    if idx < len(args):
        s = args[idx].strip()
        if len(s) >= 2 and s[0] in ["'", '"'] and s[-1] == s[0]:
            return s[1:-1]
        return s
    return ""

def get_int_arg(args, idx):
    if idx < len(args):
        s = args[idx].strip().rstrip(',')
        try:
            return int(s)
        except:
            return 0
    return 0

def parse_list_string(text):
    """Parse ['a', 'b', 'c'] into list."""
    text = text.strip()
    if not text.startswith('['):
        return []
    # Find matching close bracket
    close = find_paren_depth(text, 0, '[', ']')
    if close < 0:
        return []
    inner = text[1:close-1]
    items = split_top_level(inner)
    result = []
    for item in items:
        item = item.strip().rstrip(',')
        if len(item) >= 2 and item[0] in ["'", '"'] and item[-1] == item[0]:
            result.append(unescape(item[1:-1]))
        elif item:
            result.append(unescape(item))
    return result

def parse_checkpoint_questions(text):
    """Parse the questions list from a checkpoint_step call."""
    text = text.strip()
    if not text.startswith('['):
        bracket = text.find('[')
        if bracket < 0:
            return []
        text = text[bracket:]
    
    close = find_paren_depth(text, 0, '[', ']')
    if close < 0:
        return []
    inner = text[1:close-1]
    
    questions = []
    i = 0
    while i < len(inner):
        # Find each { }
        brace = inner.find('{', i)
        if brace < 0:
            break
        close_b = find_paren_depth(inner, brace, '{', '}')
        if close_b < 0:
            break
        obj = inner[brace+1:close_b-1]
        
        q = {}
        for field in split_top_level(obj):
            f = field.strip()
            if ':' in f:
                key, val = f.split(':', 1)
                key = key.strip().strip("'\"")
                val = val.strip().rstrip(',')
                if key == 'question':
                    v, _ = extract_string(f, f.find("'"))
                    q['question'] = unescape(v) if v else unescape(val.strip("'\""))
                elif key == 'options':
                    q['options'] = parse_list_string(val)
                elif key == 'correct' or key == 'correctIndex':
                    try:
                        q['correctIndex'] = int(val)
                    except:
                        q['correctIndex'] = 0
                elif key == 'explanation':
                    v, _ = extract_string(f, f.find("'"))
                    q['explanation'] = unescape(v) if v else unescape(val.strip("'\""))
        
        if q:
            questions.append(q)
        i = close_b
    
    return questions


# ── Read the file ─────────────────────────────────────────────────────

with open("scripts/rebuild_coremaths_modules.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find all MODULE lines
module_starts = []
for m in re.finditer(r"^MODULE(\d+)_LESSONS\s*=\s*\[\]", content, re.MULTILINE):
    module_starts.append((int(m.group(1)), m.end()))

# Build module ranges
module_ranges = {}
for idx, (num, start) in enumerate(module_starts):
    if idx + 1 < len(module_starts):
        end = module_starts[idx + 1][1]
    else:
        main_m = re.search(r"^# ── Main ─", content, re.MULTILINE)
        end = main_m.start() if main_m else len(content)
    module_ranges[num] = (start, end)

# For each module, find make_lesson calls
for mod_num in sorted(module_ranges.keys()):
    start, end = module_ranges[mod_num]
    mod_text = content[start:end]
    
    # Find all make_lesson( calls
    pos = 0
    lesson_count = 0
    while True:
        ml = mod_text.find("make_lesson(", pos)
        if ml < 0:
            break
        
        # Find the steps block - look backwards for 'steps = ['
        before_ml = mod_text[:ml]
        steps_pos = before_ml.rfind("steps = [")
        
        if steps_pos >= 0:
            # Extract steps list
            steps_text = before_ml[steps_pos + len("steps = "):]
            steps_bracket_close = find_paren_depth(steps_text, 0, '[', ']')
            
            if steps_bracket_close > 0:
                steps_inner = steps_text[1:steps_bracket_close-1]
                step_items = split_top_level(steps_inner)
                
                # Parse each step
                parsed_steps = []
                for si in step_items:
                    si = si.strip()
                    step = {}
                    
                    if si.startswith("info_step("):
                        args_text = si[len("info_step("):-1]
                        args = split_top_level(args_text)
                        if len(args) >= 2:
                            step["type"] = "info"
                            step["id"] = get_str_arg(args, 0)
                            step["content"] = unescape(get_str_arg(args, 1))
                    
                    elif si.startswith("predict_step("):
                        args_text = si[len("predict_step("):-1]
                        args = split_top_level(args_text)
                        if len(args) >= 7:
                            step["type"] = "predict"
                            step["id"] = get_str_arg(args, 0)
                            step["content"] = unescape(get_str_arg(args, 1))
                            step["predict_pattern"] = unescape(get_str_arg(args, 2))
                            step["predict_question"] = unescape(get_str_arg(args, 3))
                            step["options"] = parse_list_string(args[4])
                            step["correctIndex"] = get_int_arg(args, 5)
                            step["explanation"] = unescape(get_str_arg(args, 6))
                    
                    elif si.startswith("question_step("):
                        args_text = si[len("question_step("):-1]
                        args = split_top_level(args_text)
                        if len(args) >= 7:
                            step["type"] = "question"
                            step["id"] = get_str_arg(args, 0)
                            step["content"] = unescape(get_str_arg(args, 1))
                            step["exercise_question"] = unescape(get_str_arg(args, 2))
                            step["options"] = parse_list_string(args[3])
                            step["correctIndex"] = get_int_arg(args, 4)
                            step["explanation"] = unescape(get_str_arg(args, 5))
                    
                    elif si.startswith("checkpoint_step("):
                        args_text = si[len("checkpoint_step("):-1]
                        args = split_top_level(args_text)
                        if len(args) >= 3:
                            step["type"] = "checkpoint"
                            step["id"] = get_str_arg(args, 0)
                            step["checkpoint_title"] = unescape(get_str_arg(args, 1))
                            step["checkpoint_questions"] = parse_checkpoint_questions(args[2])
                    
                    if step and "type" in step and "id" in step:
                        parsed_steps.append(step)
                
                # Now parse the make_lesson args
                # Find the opening ( of make_lesson(
                paren_pos = ml + len("make_lesson")
                close_paren = find_paren_depth(mod_text, paren_pos, '(', ')')
                if close_paren > 0:
                    args_text = mod_text[paren_pos+1:close_paren-1]
                    ml_args = split_top_level(args_text)
                    
                    lesson_id = get_str_arg(ml_args, 0)
                    title = unescape(get_str_arg(ml_args, 1))
                    subject = get_str_arg(ml_args, 2)
                    icon = get_str_arg(ml_args, 3)
                    programme = get_str_arg(ml_args, 4)
                    diff = get_int_arg(ml_args, 5)
                    mins = get_int_arg(ml_args, 6)
                    xp_val = get_int_arg(ml_args, 7)
                    unit_id = get_str_arg(ml_args, 8)
                    
                    if lesson_id:
                        lesson_count += 1
                        print(f"  M{mod_num}: {lesson_id} - {title} ({len(parsed_steps)} steps)")
        
        pos = ml + 1
    
    print(f"  Module {mod_num}: {lesson_count} lessons")

# Since parsing the rebuild script is too complex, let me take the winning approach:
# Write all 45 lessons as good clean Python code in one shot.

print("\n\n⚠️ Complex parsing failed. Using direct generation approach instead.")
