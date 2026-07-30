"""Grade phase-challenge answers across question types."""
from __future__ import annotations

import json
import re
from typing import Any


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _tokens(s: str) -> set[str]:
    return {t for t in re.split(r"[^a-z0-9]+", _norm(s)) if t}


def grade_answer(
    *,
    question_type: str,
    correct_answer: str,
    user_answer: str,
    options: dict[str, Any] | None = None,
) -> bool:
    qtype = (question_type or "mcq").strip().lower()
    user = (user_answer or "").strip()
    correct = (correct_answer or "").strip()
    opts = options if isinstance(options, dict) else {}

    if not user or user.lower() == "timeout":
        return False

    if qtype in ("mcq", "image_mcq", "diagram_label", "scenario"):
        return _grade_mcq(user, correct, opts)

    if qtype in ("true_false", "truefalse", "tf"):
        return _norm(user) in {_norm(correct), "true" if _truthy(correct) else "false"}

    if qtype in ("fill_blank", "fill-blank", "fillblank"):
        return _grade_fill_blank(user, correct, opts)

    if qtype in ("short_answer", "short-answer", "shortanswer"):
        return _grade_short_answer(user, correct, opts)

    if qtype in ("matching", "match"):
        return _grade_matching(user, correct, opts)

    if qtype in ("ordering", "order", "sequence"):
        return _grade_ordering(user, correct, opts)

    # Default: case-insensitive string compare
    return _norm(user) == _norm(correct)


def _truthy(value: str) -> bool:
    return _norm(value) in {"true", "t", "yes", "1", "a"}


def _grade_mcq(user: str, correct: str, opts: dict[str, Any]) -> bool:
    if _norm(user) == _norm(correct):
        return True
    # Letter vs text
    letter = correct.strip().upper()[:1]
    if user.strip().upper()[:1] == letter and len(user.strip()) <= 2:
        return True
    choices = opts.get("choices") if isinstance(opts.get("choices"), dict) else opts
    if isinstance(choices, dict):
        for key, val in choices.items():
            if key in ("image", "template", "answers", "left", "right", "items", "pairs", "blanks", "hints", "accepted"):
                continue
            if not isinstance(val, (str, int, float)):
                continue
            if _norm(str(val)) == _norm(user):
                return _norm(str(key)) == _norm(correct) or str(key).upper()[:1] == letter
            if _norm(str(key)) == _norm(user):
                return str(key).upper()[:1] == letter or _norm(str(key)) == _norm(correct)
    return False


def _grade_fill_blank(user: str, correct: str, opts: dict[str, Any]) -> bool:
    expected = opts.get("answers")
    if isinstance(expected, list) and expected:
        parts = [p.strip() for p in re.split(r"[|;]+", user)]
        if len(parts) != len(expected):
            # single field joined
            parts = [user]
            if len(expected) > 1:
                return False
        return all(_norm(parts[i]) == _norm(str(expected[i])) for i in range(len(expected)))
    parts_u = [_norm(p) for p in re.split(r"[|;]+", user) if p.strip()]
    parts_c = [_norm(p) for p in re.split(r"[|;]+", correct) if p.strip()]
    return parts_u == parts_c


def _grade_short_answer(user: str, correct: str, opts: dict[str, Any]) -> bool:
    accepted = opts.get("accepted") or opts.get("accepted_answers") or []
    pool = [correct] + ([str(a) for a in accepted] if isinstance(accepted, list) else [])
    u = _norm(user)
    for cand in pool:
        c = _norm(str(cand))
        if not c:
            continue
        if u == c:
            return True
        # Soft match: user contains key tokens of expected (or vice versa for short keys)
        ct, ut = _tokens(c), _tokens(u)
        if ct and ct.issubset(ut):
            return True
        if len(c) >= 4 and (c in u or u in c):
            return True
    return False


def _parse_match_map(raw: str) -> dict[int, int] | None:
    raw = raw.strip()
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return {int(k): int(v) for k, v in data.items()}
        if isinstance(data, list):
            return {i: int(v) for i, v in enumerate(data)}
    except Exception:
        pass
    # compact "0:1,1:0,2:2"
    out: dict[int, int] = {}
    for part in raw.split(","):
        if ":" not in part:
            continue
        a, b = part.split(":", 1)
        try:
            out[int(a.strip())] = int(b.strip())
        except ValueError:
            return None
    return out or None


def _grade_matching(user: str, correct: str, opts: dict[str, Any]) -> bool:
    expected = opts.get("correct_matches")
    exp_map: dict[int, int] | None
    if isinstance(expected, list):
        exp_map = {i: int(v) for i, v in enumerate(expected)}
    else:
        exp_map = _parse_match_map(correct)
    got = _parse_match_map(user)
    if exp_map is None or got is None:
        return _norm(user) == _norm(correct)
    return exp_map == got


def _grade_ordering(user: str, correct: str, opts: dict[str, Any]) -> bool:
    expected = opts.get("correct_order")
    if isinstance(expected, list):
        exp = [_norm(str(x)) for x in expected]
    else:
        try:
            parsed = json.loads(correct)
            exp = [_norm(str(x)) for x in parsed] if isinstance(parsed, list) else [_norm(p) for p in correct.split("|")]
        except Exception:
            exp = [_norm(p) for p in re.split(r"[|;]+", correct) if p.strip()]
    try:
        parsed_u = json.loads(user)
        got = [_norm(str(x)) for x in parsed_u] if isinstance(parsed_u, list) else [_norm(p) for p in user.split("|")]
    except Exception:
        got = [_norm(p) for p in re.split(r"[|;]+", user) if p.strip()]
    return got == exp
