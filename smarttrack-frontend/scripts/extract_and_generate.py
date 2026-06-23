#!/usr/bin/env python
"""
extract_and_generate.py
───────────────────────
Reads rebuild_coremaths_modules.py as raw text, extracts lesson content for
ALL 9 modules (5 topics each = 45 lessons), and generates the TypeScript
output directly in learningContent.ts.

Bypasses Python syntax errors in the rebuild script by treating it as text.
"""

import re, sys, os

# ── Step 1: Read rebuild script ──────────────────────────────────────

script_path = "scripts/rebuild_coremaths_modules.py"
with open(script_path, "r", encoding="utf-8") as f:
    text = f.read()

lines = text.split("\n")

# ── Step 2: Find module boundaries ────────────────────────────────────

module_headers = []
for i, line in enumerate(lines):
    m = re.match(r"^# ── Module (\d+):\s*(.+?) ─", line)
    if m:
        module_headers.append((int(m.group(1)), m.group(2).strip(), i))

# Find the main section start
main_line = None
for i, line in enumerate(lines):
    if "# ── Main" in line:
        main_line = i
        break

print(f"Found {len(module_headers)} module headers")

# Extract each module's text
modules_text = {}
for idx, (num, title, start_line) in enumerate(module_headers):
    if idx + 1 < len(module_headers):
        end_line = module_headers[idx + 1][2]
    else:
        end_line = main_line if main_line else len(lines)
    
    module_text = "\n".join(lines[start_line:end_line])
    modules_text[num] = {"title": title, "text": module_text}
    print(f"  Module {num}: {title} (lines {start_line+1}-{end_line})")

# ── Step 3: Extract lesson data from each module ──────────────────────
# We'll extract: lesson_id, title, steps (with their content)
# The data is in f-string calls to make_lesson(), info_step(), etc.

def extract_str(text, start, end_markers=None):
    """Extract content between quotes, handling escaped quotes."""
    if text[start] not in ["'", '"']:
        return None, start
    
    quote = text[start]
    i = start + 1
    while i < len(text):
        if text[i] == "\\" and i + 1 < len(text):
            i += 2
            continue
        if text[i] == quote:
            return text[start+1:i], i + 1
        i += 1
    return None, len(text)

def extract_lesson_from_block(block_text):
    """Extract lesson info from a make_lesson() call."""
    lessons = []
    
    # Find all make_lesson( calls
    pos = 0
    while True:
        ml_pos = block_text.find("make_lesson(", pos)
        if ml_pos < 0:
            break
        
        # Find the matching closing paren
        depth = 1
        i = ml_pos + len("make_lesson(")
        while i < len(block_text) and depth > 0:
            if block_text[i] == "(":
                depth += 1
            elif block_text[i] == ")":
                depth -= 1
            i += 1
        
        if depth == 0:
            call_content = block_text[ml_pos + len("make_lesson("):i-1]
            
            # Now parse the arguments - they are comma-separated
            # Simple approach: split by top-level commas
            args = split_top_level_commas(call_content)
            
            if len(args) >= 16:
                lesson_id = extract_ts_str(args[0])
                title = extract_ts_str(args[1])
                subject = extract_ts_str(args[2])
                icon = extract_ts_str(args[3])
                programme = extract_ts_str(args[4])
                
                # Skip difficulty(5), minutes(6), xp(7), unit_id(8)
                # Skip prerequisites(9), shs_levels(10), suggested_level(11)
                # The steps list is arg[12]
                
                steps_text = args[12] if len(args) > 12 else ""
                
                # Extract steps
                steps = extract_steps(steps_text)
                
                lessons.append({
                    "id": lesson_id,
                    "title": title,
                    "subject": subject,
                    "icon": icon,
                    "programme": programme,
                    "steps": steps,
                })
            
            pos = i
        else:
            pos = ml_pos + len("make_lesson(")
    
    return lessons


def split_top_level_commas(text):
    """Split by commas that are not inside parentheses or brackets."""
    parts = []
    depth_paren = 0
    depth_bracket = 0
    depth_brace = 0
    current = ""
    in_single_quote = False
    in_double_quote = False
    escape = False
    
    for ch in text:
        if escape:
            current += ch
            escape = False
            continue
        
        if ch == "\\":
            current += ch
            escape = True
            continue
        
        if ch == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
            current += ch
            continue
        
        if ch == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
            current += ch
            continue
        
        if not in_single_quote and not in_double_quote:
            if ch == "(":
                depth_paren += 1
            elif ch == ")":
                depth_paren -= 1
            elif ch == "[":
                depth_bracket += 1
            elif ch == "]":
                depth_bracket -= 1
            elif ch == "{":
                depth_brace += 1
            elif ch == "}":
                depth_brace -= 1
            elif ch == "," and depth_paren == 0 and depth_bracket == 0 and depth_brace == 0:
                parts.append(current.strip())
                current = ""
                continue
        
        current += ch
    
    if current.strip():
        parts.append(current.strip())
    
    return parts


def extract_ts_str(s):
    """Extract a TypeScript string literal, removing surrounding quotes."""
    s = s.strip()
    if s.startswith("f'") or s.startswith("f\""):
        s = s[2:]
    if s.startswith("'") or s.startswith('"'):
        quote = s[0]
        # Find matching closing quote
        i = 1
        while i < len(s):
            if s[i] == "\\" and i + 1 < len(s):
                i += 2
                continue
            if s[i] == quote:
                content = s[1:i]
                # Unescape
                content = content.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")
                # Fix \\n -> \n
                content = content.replace("\\n", "\n")
                return content
            i += 1
    return s


def extract_steps(steps_text):
    """Extract step info from the steps list."""
    # Steps are inside [...] brackets. We need to find each step object.
    steps = []
    
    # Find each {...} step object
    brace_depth = 0
    step_start = -1
    
    for i, ch in enumerate(steps_text):
        if ch == "{":
            if brace_depth == 0:
                step_start = i
            brace_depth += 1
        elif ch == "}":
            brace_depth -= 1
            if brace_depth == 0 and step_start >= 0:
                step_text = steps_text[step_start:i+1]
                step = parse_step_object(step_text)
                if step:
                    steps.append(step)
                step_start = -1
    
    return steps


def parse_step_object(text):
    """Parse a TS step object like { id: 'x', type: 'info', content: '...' }."""
    step = {}
    
    # Extract id
    m = re.search(r"id:\s*'([^']*)'", text)
    if m:
        step["id"] = m.group(1)
    
    # Extract type
    m = re.search(r"type:\s*'([^']*)'", text)
    if m:
        step["type"] = m.group(1)
    
    # Extract content - this can be multi-line
    # Find content: followed by the string
    content_match = re.search(r"content:\s*\n?\s*'((?:[^'\\]|\\.)*)'", text, re.DOTALL)
    if content_match:
        content = content_match.group(1)
        # Unescape
        content = content.replace("\\'", "'").replace("\\\\", "\\").replace("\\n", "\n")
        step["content"] = content
    
    # Extract exercise question and options
    q_match = re.search(r"question:\s*'((?:[^'\\]|\\.)*)'", text, re.DOTALL)
    if q_match:
        step["exercise_question"] = q_match.group(1).replace("\\'", "'").replace("\\\\", "\\").replace("\\n", "\n")
    
    # Extract options list
    opts_match = re.search(r"options:\s*\[([^\]]*)\]", text, re.DOTALL)
    if opts_match:
        opts_text = opts_match.group(1)
        options = re.findall(r"'((?:[^'\\]|\\.)*)'", opts_text)
        step["options"] = [o.replace("\\'", "'").replace("\\\\", "\\").replace("\\n", "\n") for o in options]
    
    # Extract correctIndex
    ci_match = re.search(r"correctIndex:\s*(\d+)", text)
    if ci_match:
        step["correctIndex"] = int(ci_match.group(1))
    
    # Extract explanation
    e_match = re.search(r"explanation:\s*'((?:[^'\\]|\\.)*)'", text, re.DOTALL)
    if e_match:
        step["explanation"] = e_match.group(1).replace("\\'", "'").replace("\\\\", "\\").replace("\\n", "\n")
    
    # Checkpoint-specific fields
    cp_title = re.search(r"title:\s*'((?:[^'\\]|\\.)*)'", text, re.DOTALL)
    if cp_title and step.get("type") == "checkpoint":
        step["checkpoint_title"] = cp_title.group(1).replace("\\'", "'").replace("\\\\", "\\").replace("\\n", "\n")
    
    # Checkpoint questions
    if "questions:" in text:
        cq_start = text.find("questions:")
        cq_bracket = text.find("[", cq_start)
        if cq_bracket >= 0:
            # Find the matching bracket
            depth = 1
            i = cq_bracket + 1
            while i < len(text) and depth > 0:
                if text[i] == "[":
                    depth += 1
                elif text[i] == "]":
                    depth -= 1
                i += 1
            if depth == 0:
                qs_text = text[cq_bracket:i-1]
                questions = []
                # Parse each question object in the array
                brace_d = 0
                q_start = -1
                for j, ch in enumerate(qs_text):
                    if ch == "{":
                        if brace_d == 0:
                            q_start = j
                        brace_d += 1
                    elif ch == "}":
                        brace_d -= 1
                        if brace_d == 0 and q_start >= 0:
                            q_text = qs_text[q_start:j+1]
                            q = {}
                            qq = re.search(r"question:\s*'((?:[^'\\]|\\.)*)'", q_text, re.DOTALL)
                            if qq: q["question"] = qq.group(1).replace("\\'", "'").replace("\\\\", "\\").replace("\\n", "\n")
                            qo = re.search(r"options:\s*\[([^\]]*)\]", q_text, re.DOTALL)
                            if qo:
                                opts = re.findall(r"'((?:[^'\\]|\\.)*)'", qo.group(1))
                                q["options"] = [o.replace("\\'", "'").replace("\\\\", "\\").replace("\\n", "\n") for o in opts]
                            qc = re.search(r"correctIndex:\s*(\d+)", q_text)
                            if qc: q["correctIndex"] = int(qc.group(1))
                            qe = re.search(r"explanation:\s*'((?:[^'\\]|\\.)*)'", q_text, re.DOTALL)
                            if qe: q["explanation"] = qe.group(1).replace("\\'", "'").replace("\\\\", "\\").replace("\\n", "\n")
                            if q: questions.append(q)
                            q_start = -1
                step["checkpoint_questions"] = questions
    
    # Predict-specific fields
    p_pattern = re.search(r"pattern:\s*'((?:[^'\\]|\\.)*)'", text, re.DOTALL)
    if p_pattern:
        step["predict_pattern"] = p_pattern.group(1).replace("\\'", "'").replace("\\\\", "\\").replace("\\n", "\n")
    
    p_question = re.search(r"question:\s*'((?:[^'\\]|\\.)*)'", text, re.DOTALL)
    if p_question and step.get("type") == "predict":
        step["predict_question"] = p_question.group(1).replace("\\'", "'").replace("\\\\", "\\").replace("\\n", "\n")
    
    # PassThreshold and bonusXp for checkpoints
    pt = re.search(r"passThreshold:\s*(\d+)", text)
    if pt: step["passThreshold"] = int(pt.group(1))
    bx = re.search(r"bonusXp:\s*(\d+)", text)
    if bx: step["bonusXp"] = int(bx.group(1))
    
    return step


def convert_step_to_py(step):
    """Convert a parsed step dict to Python dict literal."""
    step_type = step.get("type", "info")
    
    if step_type == "info":
        return f"""
    i({repr(step['id'])}, {repr(step.get('content', ''))})"""
    
    elif step_type == "predict":
        return f"""
    p({repr(step['id'])}, {repr(step.get('content', ''))}, {repr(step.get('predict_pattern', ''))}, {repr(step.get('predict_question', ''))}, {repr(step.get('options', []))}, {step.get('correctIndex', 0)}, {repr(step.get('explanation', ''))})"""
    
    elif step_type == "question":
        return f"""
    q({repr(step['id'])}, {repr(step.get('content', ''))}, {repr(step.get('exercise_question', ''))}, {repr(step.get('options', []))}, {step.get('correctIndex', 0)}, {repr(step.get('explanation', ''))})"""
    
    elif step_type == "checkpoint":
        questions = step.get("checkpoint_questions", [])
        qs_str = ", ".join(
            f'{{"question": {repr(q.get("question", ""))}, "options": {repr(q.get("options", []))}, "correctIndex": {q.get("correctIndex", 0)}, "explanation": {repr(q.get("explanation", ""))}}}'
            for q in questions
        )
        return f"""
    c({repr(step['id'])}, {repr(step.get('checkpoint_title', ''))}, [{qs_str}])"""
    
    return ""


# ── Step 4: Convert all modules ────────────────────────────────────────

all_modules = {}

for mod_num in sorted(modules_text.keys()):
    mod = modules_text[mod_num]
    lessons = extract_lesson_from_block(mod["text"])
    all_modules[mod_num] = lessons
    print(f"  Module {mod_num} ({mod['title']}): extracted {len(lessons)} lessons")

# ── Step 5: Generate the output Python code ───────────────────────────

output_lines = []
output_lines.append("""#!/usr/bin/env python
# ══════════════════════════════════════════════════════════════════════════
#  ALL MODULE LESSONS — Generated from rebuild_coremaths_modules.py
# ══════════════════════════════════════════════════════════════════════════

ALL_LESSONS_TEMPLATE = []
""")

for mod_num in sorted(all_modules.keys()):
    lessons = all_modules[mod_num]
    mod = modules_text[mod_num]
    
    # Module-level info
    module_var = f"MODULE{mod_num}_LESSONS"
    
    for lesson in lessons:
        lesson_id = lesson["id"]
        title = lesson["title"]
        subject = lesson["subject"]
        icon = lesson.get("icon", "🔢")
        programme = lesson.get("programme", "Both")
        steps = lesson["steps"]
        
        # Determine difficulty, minutes, xp from step count
        step_count = len(steps)
        if step_count <= 4:
            diff, mins, xp = 1, 8, 20
        elif step_count <= 6:
            diff, mins, xp = 2, 12, 25
        else:
            diff, mins, xp = 2, 14, 30
        
        # Check for checkpoint (has checkpoint_questions) — those are harder
        has_checkpoint = any(s.get("type") == "checkpoint" and s.get("checkpoint_questions") for s in steps)
        if has_checkpoint:
            if diff == 1:
                diff, mins, xp = 2, 12, 25
            else:
                diff, mins, xp = 3, 14, 30
        
        # Build steps as Python dict calls
        steps_py = []
        for s in steps:
            s_type = s.get("type", "info")
            if s_type == "info":
                steps_py.append(f"    i({repr(s['id'])}, {repr(s.get('content', ''))})")
            elif s_type == "predict":
                steps_py.append(f"    p({repr(s['id'])}, {repr(s.get('content', ''))}, {repr(s.get('predict_pattern', ''))}, {repr(s.get('predict_question', ''))}, {repr(s.get('options', []))}, {s.get('correctIndex', 0)}, {repr(s.get('explanation', ''))})")
            elif s_type == "question":
                steps_py.append(f"    q({repr(s['id'])}, {repr(s.get('content', ''))}, {repr(s.get('exercise_question', ''))}, {repr(s.get('options', []))}, {s.get('correctIndex', 0)}, {repr(s.get('explanation', ''))})")
            elif s_type == "checkpoint":
                questions = s.get("checkpoint_questions", [])
                qs_parts = []
                for q in questions:
                    qs_parts.append(f'{{"question": {repr(q.get("question", ""))}, "options": {repr(q.get("options", []))}, "correctIndex": {q.get("correctIndex", 0)}, "explanation": {repr(q.get("explanation", ""))}}}')
                qs_str = ", ".join(qs_parts)
                steps_py.append(f"    c({repr(s['id'])}, {repr(s.get('checkpoint_title', ''))}, [{qs_str}])")
        
        steps_block = ",\n".join(steps_py)
        
        # Build unit id
        unit_id = "core-maths"
        
        # Prerequisites - derive from previous topic in module
        prev_in_module = None
        for other in lessons:
            if other["id"] < lesson["id"] and other["id"].startswith(f"coremath-m{mod_num}"):
                prev_in_module = other["id"]
        prereqs = [prev_in_module] if prev_in_module else []
        
        # Get module-level prerequisite (first lesson depends on previous module's last lesson)
        if prev_in_module is None and mod_num > 1:
            prev_mod_lessons = all_modules.get(mod_num - 1, [])
            if prev_mod_lessons:
                prereqs = [prev_mod_lessons[-1]["id"]]
        
        shs_levels = ["SHS 1"] if diff == 1 else (["SHS 2"] if diff == 2 else ["SHS 2", "SHS 3"])
        suggested_level = "SHS 1" if diff == 1 else ("SHS 2" if diff == 2 else "SHS 3")
        
        output_lines.append(f"""
ALL_LESSONS_TEMPLATE.append(L({repr(lesson_id)}, {repr(title)},
    {repr(subject)}, {repr(icon)}, {repr(programme)}, {diff}, {mins}, {xp},
    {repr(unit_id)}, {repr(prereqs)}, {repr(shs_levels)}, {repr(suggested_level)}, [
{steps_block},
]))""")

    output_lines.append(f"\n# End of Module {mod_num}\n")

# Write the generated Python code
os.makedirs("scripts", exist_ok=True)
with open("scripts/generated_lessons.py", "w", encoding="utf-8") as f:
    f.write("".join(output_lines))

print(f"\n✅ Generated {sum(len(v) for v in all_modules.values())} lesson definitions in scripts/generated_lessons.py")
