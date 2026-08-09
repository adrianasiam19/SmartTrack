"""Generate adaptive mixed-format challenge questions.

Image-first when a visual helps; otherwise text-first. LLM is primary.
Academic bank / rule fallback are last resorts after retries.

Image mismatch / retrieve failure: demote to a text question (detach image,
scrub visual language) whenever the item remains gradeable — do not reject
the whole LLM response for image metadata friction.

Internal curriculum depth:
  Phase 1 → SHS 1 only
  Phase 2 → SHS 2 only
  Phase 3 → SHS 3 with SHS 1–2 reinforcement

Learner-facing text must never mention SHS / textbook chapter references.
Learner payloads never include image attribution (scrub after validation).
"""
from __future__ import annotations

import asyncio
import json
import logging
import random
import re
from typing import Any

from app.config import settings
from app.media.educational_images import mentions_visual
from app.media.image_plan import ImagePlanner
from app.media.image_retrieval import retrieve_for_plan, retrieve_for_plan_local_only
from app.media.labelled_diagrams import labels_legend_text
from app.phases.academic_bank import select_question as select_from_bank
from app.phases.adaptive import normalize_question_text
from app.phases.curriculum_topics import (
    curriculum_gate,
    phase_curriculum_label,
    pick_curriculum_topic,
    topic_prompt_block,
)
from app.phases.question_quality import (
    fill_blank_is_self_contained,
    needs_labelled_diagram,
    visual_without_image,
)

logger = logging.getLogger(__name__)


def _dev_log_reject(rule: str, *, detail: str = "", subject: str = "", qtype: str = "") -> None:
    """Development-only rejection / demotion diagnostics (never shown to learners)."""
    logger.warning(
        "challenge_reject rule=%s subject=%s qtype=%s detail=%s",
        rule,
        subject or "-",
        qtype or "-",
        (detail or "")[:160],
    )


def _dev_log_source(source: str, *, subject: str = "", qtype: str = "", note: str = "") -> None:
    logger.info(
        "challenge_source=%s subject=%s qtype=%s %s",
        source,
        subject or "-",
        qtype or "-",
        note,
    )


def _scrub_visual_language(item: dict[str, Any]) -> dict[str, Any]:
    item["question_text"] = _strip_diagram_language(str(item.get("question_text") or ""))
    item["explanation"] = _strip_diagram_language(str(item.get("explanation") or ""))
    opts_local = item.get("options") if isinstance(item.get("options"), dict) else {}
    if opts_local.get("template"):
        opts_local = dict(opts_local)
        opts_local["template"] = _strip_diagram_language(str(opts_local["template"]))
        item["options"] = opts_local
    return item


def _demote_to_text_question(
    payload: dict[str, Any],
    *,
    reason: str,
    subject: str = "",
) -> dict[str, Any]:
    """
    Keep a usable LLM question when the image path fails.
    Remove image + visual references; convert image_* types to mcq.
    """
    qtype = str(payload.get("question_type") or "mcq")
    payload = _detach_image(payload)
    if qtype in ("image_mcq", "diagram_label"):
        payload["question_type"] = "mcq"
        qtype = "mcq"
    payload = _scrub_visual_language(payload)
    logger.info(
        "challenge_repaired action=demote_text reason=%s subject=%s qtype=%s",
        reason,
        subject or "-",
        qtype,
    )
    return payload

SUBJECT_LABELS = {
    "english": "English Language",
    "core_maths": "Core Mathematics",
    "integrated_science": "Integrated Science",
    "social_studies": "Social Studies",
}

# Internal scope only — never echo SHS labels into question_text.
PHASE_SCOPE: dict[int, str] = {
    1: (
        "Use ONLY SHS 1 (Year 1) Ghana secondary curriculum topics for this subject. "
        "Do not include SHS 2, SHS 3, or WASSCE-only items. "
        "Stay strictly inside the HARD TOPIC LOCK provided below."
    ),
    2: (
        "Use ONLY SHS 2 (Year 2) Ghana secondary curriculum topics for this subject. "
        "Do not include SHS 3-only or WASSCE-only items. "
        "Stay strictly inside the HARD TOPIC LOCK provided below."
    ),
    3: (
        "Primary focus: SHS 3 (Year 3) Ghana secondary topics. "
        "You may reinforce important SHS 1–2 concepts when the topic lock says so. "
        "Prefer exam-style application when difficulty is high (10+). "
        "Stay strictly inside the HARD TOPIC LOCK provided below."
    ),
}

QUESTION_TYPES = (
    "mcq",
    "true_false",
    "fill_blank",
    "short_answer",
    "matching",
    "ordering",
    "scenario",
    "image_mcq",
    "diagram_label",
)

TYPE_ALIASES = {
    "true-false": "true_false",
    "truefalse": "true_false",
    "tf": "true_false",
    "fill-blank": "fill_blank",
    "fillblank": "fill_blank",
    "fill-in-the-blank": "fill_blank",
    "short-answer": "short_answer",
    "shortanswer": "short_answer",
    "short-response": "short_answer",
    "match": "matching",
    "order": "ordering",
    "sequence": "ordering",
    "rank": "ordering",
    "image-mcq": "image_mcq",
    "diagram-label": "diagram_label",
    "diagram": "diagram_label",
}


def normalize_question_type(raw: str | None, fallback: str = "mcq") -> str:
    q = (raw or fallback).strip().lower().replace(" ", "_")
    q = TYPE_ALIASES.get(q, q)
    return q if q in QUESTION_TYPES else fallback


TYPE_WEIGHTS: dict[str, dict[str, int]] = {
    "integrated_science": {
        "mcq": 2,
        "true_false": 2,
        "fill_blank": 2,
        "short_answer": 2,
        "matching": 2,
        "ordering": 1,
        "scenario": 2,
        "image_mcq": 3,
        "diagram_label": 2,
    },
    "social_studies": {
        "mcq": 3,
        "true_false": 2,
        "fill_blank": 2,
        "short_answer": 2,
        "matching": 2,
        "ordering": 2,
        "scenario": 3,
        "image_mcq": 0,
        "diagram_label": 0,
    },
    "core_maths": {
        "mcq": 3,
        "true_false": 1,
        "fill_blank": 3,
        "short_answer": 3,
        "matching": 1,
        "ordering": 2,
        "scenario": 2,
        "image_mcq": 1,
        "diagram_label": 0,
    },
    "english": {
        "mcq": 2,
        "true_false": 2,
        "fill_blank": 2,
        "short_answer": 3,
        "matching": 2,
        "ordering": 2,
        "scenario": 3,
        "image_mcq": 0,
        "diagram_label": 0,
    },
}

# Free-search images are too unreliable for these subjects — text-only challenges.
# English stays text-only. Other subjects use Stage 1 visual-need analysis.
NO_IMAGE_SUBJECTS = frozenset({"english"})


SHS_LEAK_RE = re.compile(
    r"\b("
    r"SHS\s*[123]|"
    r"senior\s*high|"
    r"WASSCE(?:\s*past\s*paper)?|"
    r"WAEC(?:\s*syllabus)?|"
    r"Phase\s*[123]|"
    r"Year\s*[123]|"
    r"form\s*[123]|"
    r"your\s*textbook|"
    r"textbook\s*chapter|"
    r"syllabus"
    r")\b",
    re.I,
)

# Questions must not invent lettered labels on unlabelled stock diagrams.
FAKE_LABEL_RE = re.compile(
    r"\b("
    r"labelled\s+part|labeled\s+part|label(?:led)?\s+[A-D1-9]|"
    r"part\s+[A-D1-9]\b|structure\s+[A-D1-9]\b|letter\s+[A-D]\b|"
    r"which\s+(?:of\s+the\s+)?(?:following\s+)?label|"
    r"the\s+part\s+marked|the\s+arrow\s+(?:marked|labelled|labeled)|"
    r"indicated\s+by\s+(?:the\s+)?(?:letter|label|number)|"
    r"X,\s*Y\s*(?:and|&)\s*Z"
    r")\b",
    re.I,
)

IMAGE_RULES = (
    "IMAGE RULES (critical):\n"
    "- If a labelled Atlas diagram with A/B/C markers is provided, you MAY ask which "
    "label (A/B/C/D) matches a structure — and ONLY using those exact letters.\n"
    "- If a stock photo/diagram WITHOUT letter markers is provided, do NOT ask about "
    "labelled parts; ask what the whole figure shows.\n"
    "- Never say 'shown below/in the figure' unless an image is actually provided below.\n"
)

SELF_CONTAINED_RULES = (
    "SELF-CONTAINED RULES (critical):\n"
    "- fill_blank / short_answer / mcq must include ALL numbers, facts, and context "
    "needed to answer INSIDE question_text and/or template.\n"
    "- NEVER write 'the amount spent on labour is ___' without giving the full word "
    "problem / table / percentages in the same item.\n"
    "- NEVER refer to a chart, table, graph, or mining activity 'shown' unless an image "
    "is provided in this prompt.\n"
    "- For Core Maths fill_blank: put the full problem statement in template, e.g. "
    "'A project costs GHS 1200. Labour is 35% of the cost. Labour cost = GHS ___.'\n"
)


def _pick_question_type(
    subject: str,
    rng: random.Random,
    *,
    used_in_level: list[str] | None = None,
) -> str:
    """
    Weighted type pick with soft within-level diversity.

    Avoids a single level collapsing to all-MCQ when the LLM path is healthy.
    """
    weights = dict(TYPE_WEIGHTS.get(subject) or TYPE_WEIGHTS["integrated_science"])
    used = used_in_level or []
    counts: dict[str, int] = {}
    for t in used:
        counts[t] = counts.get(t, 0) + 1

    for t, c in counts.items():
        if t not in weights:
            continue
        if c >= 2:
            weights[t] = 0
        elif c == 1:
            weights[t] = max(0, int(weights[t]) - 2)

    # If the level is already MCQ-heavy, strongly prefer other formats.
    mcq_count = counts.get("mcq", 0) + counts.get("image_mcq", 0)
    if mcq_count >= max(1, len(used) // 2):
        for t in ("mcq", "image_mcq"):
            if t in weights:
                weights[t] = max(0, int(weights[t]) - 2)

    pool: list[str] = []
    for t, w in weights.items():
        pool.extend([t] * max(0, int(w)))
    if not pool:
        # Fall back to original weights if penalties wiped the pool
        base = TYPE_WEIGHTS.get(subject) or TYPE_WEIGHTS["integrated_science"]
        for t, w in base.items():
            pool.extend([t] * max(0, int(w)))
    return rng.choice(pool) if pool else "mcq"


def plan_types_for_subjects(subjects: list[str], rng: random.Random) -> list[str]:
    """Pre-assign diverse question types for each slot in a level."""
    planned: list[str] = []
    for subject in subjects:
        planned.append(_pick_question_type(subject, rng, used_in_level=planned))
    return planned


# Equal mix across Bloom levels (Stage 2 — cognitive balance).
BLOOM_LEVELS: tuple[str, ...] = ("recall", "understanding", "application", "analysis")

BLOOM_INSTRUCTIONS: dict[str, str] = {
    "recall": (
        "COGNITIVE LEVEL (required): RECALL (~25% of Atlas items).\n"
        "Ask the learner to remember a fact, term, definition, symbol, formula name, "
        "or simple identification.\n"
        "Keep it clear and fair — still curriculum-aligned, not trivial trivia.\n"
        "Examples of stem styles: \"What is…?\", \"Which term means…?\", "
        "\"The symbol for … is\", \"Which organelle / structure is…?\".\n"
        "Do NOT require multi-step reasoning or real-world scenarios for this item.\n"
    ),
    "understanding": (
        "COGNITIVE LEVEL (required): UNDERSTANDING (~25% of Atlas items).\n"
        "Ask the learner to explain, interpret, classify, compare, or restate a concept "
        "in their own reasoning (not bare memorisation).\n"
        "Examples: \"Which statement best explains…?\", \"What does this mean in context?\", "
        "\"Which example illustrates…?\".\n"
        "Avoid pure recall and avoid multi-step problem solving for this item.\n"
    ),
    "application": (
        "COGNITIVE LEVEL (required): APPLICATION (~25% of Atlas items).\n"
        "Ask the learner to use a concept in a concrete situation, calculation, "
        "or familiar classroom/real-life case.\n"
        "Examples: word problems, applying a rule/formula, choosing the correct method "
        "for a given situation.\n"
        "Provide all numbers and context inside the question. One clear application step "
        "is enough — do not make it an analysis essay.\n"
    ),
    "analysis": (
        "COGNITIVE LEVEL (required): ANALYSIS (~25% of Atlas items).\n"
        "Ask the learner to break down information, find relationships, diagnose an error, "
        "compare causes/effects, or justify the best conclusion from given evidence.\n"
        "Examples: \"Which factor best explains…?\", \"Where is the mistake…?\", "
        "\"Based on the evidence, which conclusion follows?\".\n"
        "Include enough evidence in the stem. Stay focused — one analytical judgement, "
        "not an open essay.\n"
    ),
}


def _pick_bloom_level(rng: random.Random) -> str:
    """Uniform 25% recall / understanding / application / analysis."""
    return rng.choice(BLOOM_LEVELS)


def _bloom_prompt_block(level: str) -> str:
    return BLOOM_INSTRUCTIONS.get(level) or BLOOM_INSTRUCTIONS["understanding"]


# Never show study-habit / meta / textbook-navigation stems to learners.
_UNSAFE_STEM_RE = re.compile(
    r"(?i)("
    r"\[\s*[^\]\n]{0,80}\bdifficulty\s*\d+\s*\]|"
    r"most reliable next step when solving|"
    r"approach best shows careful reasoning|"
    r"habit most improves accuracy|"
    r"how should a careful student check|"
    r"skip the problem and guess|"
    r"break it into steps and check your work|"
    r"copy a random answer|"
    r"\b(section|chapter|unit)\s+\d+\b|"
    r"\b(exercise|page)\s+\d+\b|"
    r"\bfrom (the )?(textbook|syllabus|workbook)\b|"
    r"\bin your textbook\b|"
    r"\bopen (your )?social studies\b|"
    r"\bwhat would you read\b"
    r")"
)

_META_PREFIX_RE = re.compile(
    r"(?i)^\s*\[(?:english|core\s*math(?:ematics)?|integrated\s*science|social\s*studies|"
    r"[^\]]{1,40})\s*[·•|\-]\s*difficulty\s*\d+\]\s*"
)


def is_unsafe_learner_question(payload: dict[str, Any] | None) -> bool:
    """True for filler/meta/textbook-nav items that must never reach learners."""
    if not payload:
        return True
    text = str(payload.get("question_text") or "")
    if _UNSAFE_STEM_RE.search(text):
        return True
    opts = payload.get("options") if isinstance(payload.get("options"), dict) else {}
    choices = opts.get("choices") if isinstance(opts.get("choices"), dict) else {}
    blob = " ".join(str(v) for v in choices.values())
    if _UNSAFE_STEM_RE.search(blob):
        return True
    # Generic study-habit MCQ fingerprint (old emergency fallback)
    if (
        "skip the problem and guess" in blob.lower()
        and "break it into steps" in blob.lower()
    ):
        return True
    return False


# Real curriculum-anchored last-resort items (no meta labels, no study-habit fluff).
_CURRICULUM_FALLBACKS: dict[str, list[dict[str, Any]]] = {
    "integrated_science": [
        {
            "question_text": (
                "Water moves from a dilute solution to a concentrated solution "
                "through a selectively permeable membrane. Which process is this?"
            ),
            "choices": {
                "A": "Diffusion of sugar only",
                "B": "Osmosis",
                "C": "Photosynthesis",
                "D": "Condensation",
            },
            "correct_answer": "B",
            "explanation": "Osmosis is the movement of water across a selectively permeable membrane.",
        },
        {
            "question_text": (
                "Which gas do green plants release into the air during photosynthesis?"
            ),
            "choices": {
                "A": "Carbon dioxide",
                "B": "Nitrogen",
                "C": "Oxygen",
                "D": "Hydrogen",
            },
            "correct_answer": "C",
            "explanation": "Photosynthesis releases oxygen as a product.",
        },
        {
            "question_text": (
                "In a simple series circuit with one cell and one bulb, what is the "
                "main role of the cell?"
            ),
            "choices": {
                "A": "To increase resistance only",
                "B": "To provide electrical energy",
                "C": "To measure current",
                "D": "To store light",
            },
            "correct_answer": "B",
            "explanation": "The cell supplies electrical energy to the circuit.",
        },
    ],
    "core_maths": [
        {
            "question_text": "What is 25% of 80?",
            "choices": {"A": "15", "B": "20", "C": "25", "D": "40"},
            "correct_answer": "B",
            "explanation": "25% of 80 = 0.25 × 80 = 20.",
        },
        {
            "question_text": "Simplify the fraction 8/12 to its lowest terms.",
            "choices": {"A": "4/8", "B": "2/3", "C": "3/4", "D": "8/12"},
            "correct_answer": "B",
            "explanation": "Divide numerator and denominator by 4 to get 2/3.",
        },
        {
            "question_text": (
                "On a number line, which integer is halfway between −2 and 4?"
            ),
            "choices": {"A": "0", "B": "1", "C": "2", "D": "3"},
            "correct_answer": "B",
            "explanation": "The midpoint is (−2 + 4) / 2 = 1.",
        },
    ],
    "social_studies": [
        {
            "question_text": (
                "Which practice best improves environmental sanitation in a community?"
            ),
            "choices": {
                "A": "Dumping refuse in open drains",
                "B": "Proper waste disposal and cleaning surroundings",
                "C": "Burning plastics in classrooms",
                "D": "Blocking gutters with solid waste",
            },
            "correct_answer": "B",
            "explanation": "Safe disposal and cleanliness reduce disease and pollution.",
        },
        {
            "question_text": (
                "Ghana shares a land border with which of these countries?"
            ),
            "choices": {
                "A": "Kenya",
                "B": "Côte d'Ivoire (Ivory Coast)",
                "C": "Egypt",
                "D": "South Africa",
            },
            "correct_answer": "B",
            "explanation": "Ghana borders Côte d'Ivoire, Burkina Faso, and Togo.",
        },
        {
            "question_text": (
                "On a map, what does the scale mainly help a reader do?"
            ),
            "choices": {
                "A": "Choose map colours",
                "B": "Convert map distances to real distances",
                "C": "Name the capital city",
                "D": "Find the author of the map",
            },
            "correct_answer": "B",
            "explanation": "Scale relates distances on the map to distances on the ground.",
        },
    ],
    "english": [
        {
            "question_text": (
                "In the sentence \"The tired farmer harvested the maize,\" which word "
                "is an adjective?"
            ),
            "choices": {
                "A": "farmer",
                "B": "tired",
                "C": "harvested",
                "D": "maize",
            },
            "correct_answer": "B",
            "explanation": "\"Tired\" describes the farmer, so it is an adjective.",
        },
        {
            "question_text": (
                "Which sentence is punctuated correctly?"
            ),
            "choices": {
                "A": "Where is the book.",
                "B": "Where is the book?",
                "C": "Where is the book!",
                "D": "Where is the book,",
            },
            "correct_answer": "B",
            "explanation": "A direct question ends with a question mark.",
        },
        {
            "question_text": (
                "What is the main idea of a short passage mainly about?"
            ),
            "choices": {
                "A": "One minor detail only",
                "B": "The overall point the writer wants you to understand",
                "C": "The longest word in the passage",
                "D": "The page number",
            },
            "correct_answer": "B",
            "explanation": "The main idea is the central point of the text.",
        },
    ],
}


def _fallback_question(
    subject: str,
    effective_difficulty: int,
    salt: int = 0,
    *,
    phase_number: int = 1,
) -> dict[str, Any]:
    """
    Last-resort item: real curriculum MCQ only.
    Never emit meta tags like [Subject · difficulty N] or study-habit fillers.
    """
    pool = list(_CURRICULUM_FALLBACKS.get(subject) or _CURRICULUM_FALLBACKS["english"])
    # Prefer topic-aligned pack when available
    try:
        topic = pick_curriculum_topic(phase_number, subject, random.Random(salt + 17))
        if topic and topic.get("topic"):
            # Stable pick within subject pack; salt rotates variants
            pass
    except Exception:
        pass
    item = pool[salt % len(pool)]
    return {
        "question_text": str(item["question_text"]),
        "question_type": "mcq",
        "options": {"choices": dict(item["choices"])},
        "correct_answer": str(item["correct_answer"]),
        "explanation": str(item.get("explanation") or ""),
        "difficulty": int(effective_difficulty),
        "source": "fallback",
        "curriculum_topic": "curriculum_fallback",
    }


def _pick_target_level(phase_number: int, effective_difficulty: int, rng: random.Random) -> str:
    """Internal depth tag for the model — never shown to learners."""
    if phase_number <= 1:
        return "SHS 1"
    if phase_number == 2:
        return "SHS 2"
    if effective_difficulty >= 10:
        return rng.choice(["SHS 3", "SHS 3 exam application"])
    return rng.choice(["SHS 3", "SHS 1 reinforcement", "SHS 2 reinforcement"])


def _schema_instructions(qtype: str, *, has_image: bool, labelled: bool = False) -> str:
    common = (
        "Return ONLY JSON. Never mention SHS, WAEC, WASSCE past papers, textbook chapters, "
        "or 'what you learned in year X' in question_text or options. "
        "Assess conceptual understanding, reasoning, or real-world application. "
        "Include keys: question_text, question_type, explanation, image_query "
        "(usually null when an image is already provided).\n"
        f"{SELF_CONTAINED_RULES}"
    )
    if has_image:
        common += "\n" + IMAGE_RULES
        if labelled:
            common += (
                "\nA LABELLED diagram with arrows A–D is provided. "
                "Ask which letter matches a named structure using those letters only.\n"
            )

    if qtype in ("mcq", "scenario", "image_mcq", "diagram_label"):
        extra = (
            f'question_type must be "{qtype}".\n'
            "Also include: choices (object A-D), correct_answer (letter A-D).\n"
        )
        return f"{common}\n{extra}"
    if qtype == "true_false":
        return f"{common}\nquestion_type must be \"true_false\".\nInclude correct_answer as \"true\" or \"false\"."
    if qtype == "fill_blank":
        return (
            f"{common}\n"
            'question_type must be "fill_blank".\n'
            "template MUST contain the FULL problem (all given data + ___ blanks). "
            "question_text can be a short instruction like 'Complete the statement.' "
            "Include answers (string array), hints (optional). "
            "correct_answer = answers joined with | ."
        )
    if qtype == "short_answer":
        return (
            f"{common}\n"
            'question_type must be "short_answer".\n'
            "Include the full problem in question_text. "
            "Include correct_answer and accepted (array of alternates)."
        )
    if qtype == "matching":
        return (
            f"{common}\n"
            'question_type must be "matching".\n'
            "Return JSON with exactly this shape:\n"
            '{"question_type":"matching","question_text":"...","left":["L1","L2"],'
            '"right":["R1","R2"],"correct_matches":[1,0],'
            '"instruction":"Match each item.","explanation":"..."}\n'
            "correct_matches[i] = index in right for left[i] (0-based). "
            "left and right must have the same length (2–5)."
        )
    if qtype == "ordering":
        return (
            f"{common}\n"
            'question_type must be "ordering".\n'
            "Return JSON with exactly this shape:\n"
            '{"question_type":"ordering","question_text":"Arrange in the correct order.",'
            '"items":["first step","second step","third step"],'
            '"explanation":"..."}\n'
            "items MUST be a string array in the CORRECT order (3–6 unique strings). "
            "Do NOT use numeric index arrays. Do NOT put the steps only inside question_text."
        )
    if qtype in ("mcq", "scenario", "image_mcq", "diagram_label"):
        return (
            f"{common}\n"
            f'question_type must be "{qtype}".\n'
            "Return choices as an object with keys A,B,C,D (four distinct options). "
            'correct_answer must be exactly one of "A","B","C","D" and that letter '
            "MUST exist in choices. explanation must justify that same letter."
        )
    return common


def _sanitize_learner_text(text: str) -> str:
    if not text:
        return text
    cleaned = _META_PREFIX_RE.sub("", text)
    cleaned = SHS_LEAK_RE.sub("your studies", cleaned)
    cleaned = re.sub(r"\bSHS\b", "", cleaned, flags=re.I)
    return cleaned.strip()


def _asks_for_fake_labels(text: str) -> bool:
    return bool(FAKE_LABEL_RE.search(text or ""))


def _as_string_list(value: Any, *, max_items: int = 8) -> list[str]:
    """Normalize LLM list/dict payloads into clean unique string items."""
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                value = parsed
            else:
                return [text]
        except Exception:
            return [text]
    if isinstance(value, dict):
        # {"1":"Wash","2":"Rinse"} or {"a":"..."}
        try:
            ordered_keys = sorted(value.keys(), key=lambda k: int(str(k)))
        except Exception:
            ordered_keys = list(value.keys())
        value = [value[k] for k in ordered_keys]
    if not isinstance(value, list):
        return [str(value).strip()] if str(value).strip() else []

    out: list[str] = []
    seen: set[str] = set()
    for item in value:
        if isinstance(item, dict):
            text = str(
                item.get("text")
                or item.get("label")
                or item.get("value")
                or item.get("item")
                or ""
            ).strip()
        else:
            text = str(item).strip()
        if not text:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(_sanitize_learner_text(text))
        if len(out) >= max_items:
            break
    return out


def _extract_mcq_choices(parsed: dict[str, Any]) -> dict[str, str]:
    """Accept flat, nested, or list MCQ option shapes from the LLM."""
    raw = parsed.get("choices")
    if raw is None:
        raw = parsed.get("options")

    # Nested: options: { choices: {A:..., B:...} }
    if isinstance(raw, dict) and "choices" in raw and isinstance(raw["choices"], (dict, list)):
        raw = raw["choices"]

    if isinstance(raw, list):
        raw = {chr(65 + i): str(o) for i, o in enumerate(raw[:4])}

    letter_choices: dict[str, str] = {}
    if isinstance(raw, dict):
        for key, val in raw.items():
            letter = str(key).strip().upper()[:1]
            if letter not in "ABCD":
                continue
            if isinstance(val, dict):
                text = str(val.get("text") or val.get("label") or val.get("value") or "").strip()
            else:
                text = str(val).strip()
            if not text:
                continue
            letter_choices[letter] = _sanitize_learner_text(text)
    return letter_choices


def _resolve_mcq_correct(raw_correct: str, letter_choices: dict[str, str]) -> str:
    """Map prose / index / letter answers onto a real choice key."""
    raw = (raw_correct or "").strip()
    if not letter_choices:
        return ""

    if not raw:
        return next(iter(letter_choices.keys()))

    upper = raw.upper().strip()
    if upper[:1] in letter_choices and (len(upper) == 1 or upper[:2] in {"A.", "B.", "C.", "D."}):
        return upper[:1]

    # 1-based / 0-based numeric index
    if raw.isdigit():
        idx = int(raw)
        letters = sorted(letter_choices.keys())
        if 1 <= idx <= len(letters):
            return letters[idx - 1]
        if 0 <= idx < len(letters):
            return letters[idx]

    # Match against choice text
    target = re.sub(r"\s+", " ", raw.lower())
    for letter, text in letter_choices.items():
        if re.sub(r"\s+", " ", text.lower()) == target:
            return letter
        if target and target in text.lower():
            return letter

    # Last resort: first letter only if it is a real choice
    if upper[:1] in letter_choices:
        return upper[:1]
    return ""


def _coerce_options(qtype: str, parsed: dict[str, Any]) -> tuple[dict[str, Any], str]:
    correct = str(parsed.get("correct_answer") or "").strip()
    options: dict[str, Any] = {}

    if qtype in ("mcq", "scenario", "image_mcq", "diagram_label"):
        letter_choices = _extract_mcq_choices(parsed)
        options = {"choices": letter_choices, **letter_choices}
        correct = _resolve_mcq_correct(correct, letter_choices)

    elif qtype == "true_false":
        options = {"choices": {"A": "True", "B": "False"}, "A": "True", "B": "False"}
        c = correct.lower()
        if c in ("a", "true", "t", "yes", "1"):
            correct = "true"
        elif c in ("b", "false", "f", "no", "0"):
            correct = "false"
        else:
            # Infer from explanation / text if model omitted it
            blob = f"{parsed.get('explanation') or ''} {correct}".lower()
            correct = "false" if "false" in blob and "true" not in blob.split("false")[0][-20:] else (
                "true" if c else "true"
            )

    elif qtype == "fill_blank":
        answers = _as_string_list(parsed.get("answers"), max_items=4)
        if not answers and correct:
            answers = [p.strip() for p in re.split(r"[|;]+", correct) if p.strip()]
        template = str(
            parsed.get("template") or parsed.get("question_text") or ""
        ).strip()
        # Normalize any run of 3+ underscores to exactly ___
        template = re.sub(r"_{3,}", "___", template)
        blank_count = len(re.findall(r"___", template))
        if blank_count == 0 and answers:
            template = f"{template} ___".strip() if template else "___"
            blank_count = 1
        if answers and blank_count and len(answers) != blank_count:
            # Prefer blank count; pad/truncate answers to match blanks
            if len(answers) < blank_count:
                answers = answers + [answers[-1]] * (blank_count - len(answers))
            else:
                answers = answers[:blank_count]
        options = {
            "template": _sanitize_learner_text(template),
            "answers": answers,
            "hints": _as_string_list(parsed.get("hints"), max_items=3),
        }
        correct = "|".join(answers)

    elif qtype == "short_answer":
        accepted = parsed.get("accepted") or parsed.get("accepted_answers") or []
        if isinstance(accepted, str):
            accepted = [p.strip() for p in re.split(r"[,|;]+", accepted) if p.strip()]
        elif not isinstance(accepted, list):
            accepted = [str(accepted)] if accepted else []
        accepted = [str(a).strip() for a in accepted if str(a).strip()]
        options = {"accepted": accepted}
        correct = correct or (accepted[0] if accepted else "")

    elif qtype == "matching":
        left = _as_string_list(
            parsed.get("left") or parsed.get("left_items") or parsed.get("terms"),
            max_items=5,
        )
        right = _as_string_list(
            parsed.get("right") or parsed.get("right_items") or parsed.get("definitions"),
            max_items=5,
        )
        matches_raw = parsed.get("correct_matches") or parsed.get("matches") or []
        matches: list[int] = []
        if isinstance(matches_raw, dict):
            try:
                for i in range(len(left)):
                    matches.append(int(matches_raw.get(str(i), matches_raw.get(i, -1))))
            except Exception:
                matches = []
        elif isinstance(matches_raw, list):
            for m in matches_raw[: len(left)]:
                try:
                    matches.append(int(m))
                except Exception:
                    break
        # Drop invalid indices
        if right and matches:
            matches = [m for m in matches if 0 <= m < len(right)]
            if len(matches) != len(left):
                matches = []
        options = {
            "left": left,
            "right": right,
            "correct_matches": matches,
            "instruction": _sanitize_learner_text(
                str(parsed.get("instruction") or "Match each item to its pair.")
            ),
        }
        correct = ",".join(f"{i}:{matches[i]}" for i in range(len(matches)))

    elif qtype == "ordering":
        items = _as_string_list(
            parsed.get("items")
            or parsed.get("order")
            or parsed.get("steps")
            or parsed.get("sequence"),
            max_items=6,
        )
        correct_order_raw = parsed.get("correct_order")
        # Hub-style: items shuffled + correct_order as index array
        if (
            items
            and isinstance(correct_order_raw, list)
            and correct_order_raw
            and all(isinstance(x, (int, float)) or str(x).isdigit() for x in correct_order_raw)
        ):
            try:
                ordered = [items[int(i)] for i in correct_order_raw if 0 <= int(i) < len(items)]
                if len(ordered) == len(items):
                    items = ordered
            except Exception:
                pass
        elif not items:
            items = _as_string_list(correct_order_raw, max_items=6)
        if not items and correct:
            try:
                parsed_correct = json.loads(correct)
                items = _as_string_list(parsed_correct, max_items=6)
            except Exception:
                items = _as_string_list(re.split(r"[|;]+", correct), max_items=6)
        options = {"items": items, "correct_order": list(items)}
        correct = json.dumps(items)

    else:
        letter_choices = _extract_mcq_choices(parsed)
        options = {"choices": letter_choices, **letter_choices}
        correct = _resolve_mcq_correct(correct, letter_choices)

    return options, correct[:2000]


def _structure_valid(qtype: str, options: dict[str, Any], correct: str, text: str) -> bool:
    """Reject only incomplete / ungradeable items (keep good educational content)."""
    if not (text or "").strip():
        return False
    if qtype in ("mcq", "scenario", "image_mcq", "diagram_label"):
        choices = options.get("choices") if isinstance(options.get("choices"), dict) else {}
        if len(choices) < 2:
            return False
        if not correct or correct not in choices:
            return False
        # Allow 2+ options (true/false-style MCQs are valid educational items)
        return True
    if qtype == "true_false":
        return correct in ("true", "false")
    if qtype == "fill_blank":
        answers = options.get("answers") if isinstance(options.get("answers"), list) else []
        template = str(options.get("template") or "")
        if not answers or not all(str(a).strip() for a in answers):
            return False
        blanks = len(re.findall(r"___", template))
        return blanks >= 1 and blanks == len(answers)
    if qtype == "short_answer":
        return bool(correct.strip())
    if qtype == "matching":
        left = options.get("left") if isinstance(options.get("left"), list) else []
        right = options.get("right") if isinstance(options.get("right"), list) else []
        matches = options.get("correct_matches") if isinstance(options.get("correct_matches"), list) else []
        if len(left) < 2 or len(right) < 2:
            return False
        if len(matches) != len(left):
            return False
        return all(isinstance(m, int) and 0 <= m < len(right) for m in matches)
    if qtype == "ordering":
        items = options.get("items") if isinstance(options.get("items"), list) else []
        if len(items) < 2:
            return False
        if any(not str(x).strip() for x in items):
            return False
        try:
            parsed = json.loads(correct)
            return isinstance(parsed, list) and [str(x) for x in parsed] == [str(x) for x in items]
        except Exception:
            return False
    return bool(correct.strip())


def _align_type_to_payload(requested: str, claimed: str, parsed: dict[str, Any]) -> str:
    """
    Prefer the requested challenge type when the LLM claims a different type
    but the payload clearly matches the request (or lacks the claimed structure).
    """
    claimed_n = normalize_question_type(claimed, fallback=requested)
    requested_n = normalize_question_type(requested, fallback="mcq")
    if claimed_n == requested_n:
        return requested_n

    # If we asked for short_answer/fill_blank/ordering/matching, keep it unless
    # the payload is a fully valid MCQ.
    mcq_choices = _extract_mcq_choices(parsed)
    if requested_n in ("short_answer", "fill_blank", "ordering", "matching", "true_false"):
        if claimed_n in ("mcq", "scenario", "image_mcq", "diagram_label") and len(mcq_choices) < 2:
            return requested_n
        return requested_n

    # If we asked for MCQ but model returned a rich interactive payload, honour it
    if requested_n in ("mcq", "scenario", "image_mcq", "diagram_label"):
        if claimed_n == "ordering" and _as_string_list(parsed.get("items"), max_items=6):
            return "ordering"
        if claimed_n == "matching" and (
            _as_string_list(parsed.get("left"), max_items=5)
            or _as_string_list(parsed.get("left_items"), max_items=5)
        ):
            return "matching"
        if claimed_n == "short_answer" and not mcq_choices:
            return "short_answer"
    return claimed_n


def _bind_image(payload: dict[str, Any], image: dict[str, Any] | None) -> dict[str, Any]:
    if not image:
        return payload
    from app.media.learner_media import to_learner_image

    # Stage 5 — challenges receive learner-safe image only (no attribution/source/license)
    safe = to_learner_image(image)
    if not safe:
        return payload
    opts = dict(payload.get("options") or {})
    # Preserve educational legend if already prepared on the full image dict
    if isinstance(image.get("legend"), dict) and "legend" not in safe:
        safe = {**safe, "legend": image["legend"]}
    opts["image"] = safe
    payload["options"] = opts
    payload["image"] = safe
    return payload


def _strip_diagram_language(text: str) -> str:
    text = re.sub(
        r"(?i)\b(study|look at|observe|examine)\s+the\s+"
        r"(diagram|figure|image|picture|map|graph|illustration|scene)\s*"
        r"(below|above|shown|described)?[,:]?\s*",
        "",
        text,
    )
    text = re.sub(
        r"(?i)\bthe\s+(diagram|figure|image|illustration)\s+shows\s+",
        "Regarding this concept: ",
        text,
    )
    text = re.sub(
        r"(?i)\b(this|the)\s+(illustration|diagram|figure|image|picture)\b",
        "this description",
        text,
    )
    return text.strip()


def _detach_image(payload: dict[str, Any]) -> dict[str, Any]:
    """Remove a bound image and any legend that depended on it."""
    payload.pop("image", None)
    opts = payload.get("options") if isinstance(payload.get("options"), dict) else None
    if opts:
        opts = dict(opts)
        opts.pop("image", None)
        opts.pop("legend", None)
        payload["options"] = opts
    return payload


def _image_matches_text(image: dict[str, Any], text: str, concept: str = "") -> bool:
    """Require real keyword overlap so we never show an unrelated figure."""
    if (image.get("source") or "") == "atlas_svg":
        # Atlas figures are authored for known topics — still check for hard conflicts
        return not _image_question_conflict(image, text)
    blob = f"{image.get('alt') or ''} {image.get('url') or ''} {image.get('concept') or ''}".lower()
    stop = {
        "the", "and", "for", "with", "from", "that", "this", "diagram", "figure",
        "illustration", "educational", "image", "picture", "scene", "labelled",
        "labeled", "africa", "ghana", "study", "shown", "below", "above",
    }
    raw = f"{concept} {text}"
    tokens = {
        t for t in re.split(r"[^a-z0-9]+", raw.lower())
        if len(t) > 3 and t not in stop
    }
    if not tokens:
        return False
    hits = sum(1 for t in tokens if t in blob)
    if hits < 2:
        return False
    return not _image_question_conflict(image, text)


def _image_question_conflict(image: dict[str, Any], text: str) -> bool:
    """True when the question topic and figure title clearly disagree."""
    q = (text or "").lower()
    img = f"{image.get('alt') or ''} {image.get('key') or ''}".lower()
    pairs = [
        (
            r"\b(plane\s+mirror|incident\s+ray|angle of incidence|ray of light)\b",
            r"\b(lake|mountain|landscape|forest|sunset|scenic|waterfall)\b",
        ),
        (
            r"\b(pie\s*chart|bar\s*chart|histogram|number\s*line)\b",
            r"\b(flower|landscape|portrait|animal|mountain|lake)\b",
        ),
        (
            r"\b(plant\s+cell|chloroplast|vacuole)\b",
            r"\b(animal\s+cell|heart|neuron|circuit|mirror)\b",
        ),
        (
            r"\b(heart|circulatory|atrium|ventricle)\b",
            r"\b(plant\s+cell|neuron|circuit|mirror|pie\s*chart)\b",
        ),
    ]
    for q_re, img_re in pairs:
        if re.search(q_re, q, re.I) and re.search(img_re, img, re.I):
            return True
    return False


def _legend_for_image(image: dict[str, Any], *, labelled: bool) -> dict[str, str] | None:
    """Legend must describe the bound figure — never an unrelated curriculum focus."""
    if labelled and image.get("labels"):
        return {
            "title": "Diagram labels",
            "hint": labels_legend_text(image),
        }
    chart = image.get("chart_data")
    if isinstance(chart, dict) and chart:
        bits = ", ".join(f"{k}: {v}" for k, v in chart.items())
        return {
            "title": "Read from the chart",
            "hint": bits,
        }
    alt = str(image.get("alt") or "").strip()
    if alt:
        return {
            "title": "What the figure shows",
            "hint": alt,
        }
    return None



async def _deepseek_json(messages: list[dict[str, str]], *, temperature: float = 0.75) -> dict[str, Any] | None:
    from app.llm.deepseek_client import deepseek_message_content

    content = await deepseek_message_content(
        messages,
        temperature=temperature,
        purpose="challenge_question",
    )
    if not content:
        return None
    return _parse_json(content)


async def _llm_question(
    *,
    phase_number: int,
    level_number: int,
    subject: str,
    effective_difficulty: int,
    performance_summary: str,
    question_budget: int,
    exclude_texts: set[str],
    rng: random.Random,
    forced_type: str | None = None,
) -> dict[str, Any] | None:
    if not settings.DEEPSEEK_API_KEY:
        return None

    from app.llm.deepseek_client import llm_circuit_open

    # Network to DeepSeek is down — skip the whole LLM+planner path immediately.
    if llm_circuit_open():
        return None

    label = SUBJECT_LABELS.get(subject, subject)
    scope = PHASE_SCOPE.get(phase_number, PHASE_SCOPE[1])
    target = _pick_target_level(phase_number, effective_difficulty, rng)
    curriculum_tag = phase_curriculum_label(phase_number)
    qtype = forced_type or _pick_question_type(subject, rng)
    topic = pick_curriculum_topic(phase_number, subject, rng)
    bloom = _pick_bloom_level(rng)

    qtype_l = (qtype or "").lower()
    # English: never attach images (search quality is too weak for language arts).
    if subject in NO_IMAGE_SUBJECTS:
        if qtype_l in ("image_mcq", "diagram_label"):
            qtype = "mcq"
            qtype_l = "mcq"

    prefer_labels = qtype_l in ("diagram_label",) or (
        subject == "integrated_science" and qtype_l == "image_mcq" and rng.random() < 0.45
    )

    # Challenge image mode (Option B default = local_only):
    #   off / FAST_SKIP — never attach images
    #   local_only — Atlas SVG + existing cache only (no live search, no image LLM planner)
    #   full — legacy live retrieve path
    images_mode = str(
        getattr(settings, "CHALLENGE_IMAGES_MODE", "local_only") or "local_only"
    ).strip().lower()
    if images_mode not in {"off", "local_only", "full"}:
        # Unknown / typo values must not silently enable live network search.
        images_mode = "local_only"
    if bool(getattr(settings, "CHALLENGE_FAST_SKIP_IMAGES", False)):
        images_mode = "off"

    topic_blob = (
        f"{topic.get('topic') or ''} {topic.get('focus') or ''} {topic.get('image_query') or ''}"
        if topic
        else ""
    )

    from app.media.content_analysis import analyze_visual_need, analyze_visual_need_rules

    if images_mode == "off" or subject in NO_IMAGE_SUBJECTS:
        visual_decision = analyze_visual_need_rules(
            subject=SUBJECT_LABELS.get(subject, subject),
            title=str((topic or {}).get("topic") or label),
            context=topic_blob,
            question_type="mcq",
        )
        visual_decision.needed = False
    elif images_mode == "local_only":
        # Rules only — never call LLM content-analysis for visuals on the hot path.
        visual_decision = analyze_visual_need_rules(
            subject=SUBJECT_LABELS.get(subject, subject),
            title=str((topic or {}).get("topic") or label),
            context=topic_blob,
            question_type=qtype_l,
        )
    else:
        visual_decision = await analyze_visual_need(
            subject=SUBJECT_LABELS.get(subject, subject),
            title=str((topic or {}).get("topic") or label),
            context=topic_blob,
            question_type=qtype_l,
        )

    wants_image = (
        subject not in NO_IMAGE_SUBJECTS
        and images_mode != "off"
        and bool(visual_decision.needed)
    )

    # Local-only / off: sync curriculum plan only (no ImagePlanner LLM).
    # Full mode may use the richer planner when a visual is wanted.
    if wants_image and images_mode == "full":
        plan = await ImagePlanner.plan_for_challenge(
            subject=SUBJECT_LABELS.get(subject, subject),
            topic=topic,
            question_type=qtype_l,
            prefer_labels=prefer_labels,
            topic_hint=visual_decision.topic_hint
            or str((topic or {}).get("topic") or label),
        )
    else:
        plan = ImagePlanner.plan_from_curriculum_topic(
            topic,
            subject=subject,
            requires_labels=prefer_labels,
            question_type=qtype,
        )
        plan.needed = bool(wants_image)
        if not wants_image and qtype_l in ("image_mcq", "diagram_label"):
            qtype = "mcq"
            qtype_l = "mcq"

    image: dict[str, Any] | None = None
    labelled = False
    image_block = ""
    if plan.needed and wants_image:
        try:
            if images_mode == "local_only":
                # Instant path: never wait on Wikimedia/Pixabay.
                image = await retrieve_for_plan_local_only(plan)
            elif images_mode == "full":
                image = await asyncio.wait_for(retrieve_for_plan(plan), timeout=9.0)
            else:
                image = None
        except asyncio.TimeoutError:
            logger.info(
                "Image retrieval timed out for subject=%s topic=%s mode=%s",
                subject,
                plan.concept,
                images_mode,
            )
            image = None
        except Exception:
            logger.debug(
                "Image attach skipped subject=%s mode=%s",
                subject,
                images_mode,
                exc_info=True,
            )
            image = None

        labelled = bool(image and (image.get("source") == "atlas_svg" or image.get("labels")))
        if labelled:
            qtype = "diagram_label"
        elif not image and qtype_l in ("image_mcq", "diagram_label"):
            # No free image → stay text; never fail the question.
            qtype = "mcq"
            qtype_l = "mcq"

    if image:
        image_block = (
            "CRITICAL IMAGE ALIGNMENT RULES (image attached from local SVG/cache):\n"
            "An educational figure is already selected. Write the question about THIS "
            "figure only — do not invent a different diagram.\n"
            "Open with a natural stem such as \"Study the diagram above…\" when it fits.\n"
            f"- Concept: {plan.concept}\n"
            f"- Image title/alt: {image.get('alt')}\n"
            f"- Source: {image.get('source')}\n"
        )
        if image.get("chart_data"):
            image_block += f"- Chart values: {image.get('chart_data')}\n"
            image_block += (
                "Ask a question that can be answered ONLY from these chart values.\n"
            )
        if labelled and image.get("labels"):
            image_block += (
                f"- Label key: {labels_legend_text(image)}\n"
                "You MUST ask which letter (A/B/C/D) matches a structure from that key.\n"
                "correct_answer must be the letter.\n"
            )
        else:
            image_block += (
                "Do NOT ask about lettered labels on this unlabelled figure.\n"
                "Do NOT mention structures that are not visible in the image title/alt.\n"
            )
        if qtype == "fill_blank":
            qtype = "image_mcq" if not labelled else "diagram_label"

    avoid = ""
    if exclude_texts:
        samples = list(exclude_texts)[-24:]
        avoid = (
            "Do NOT repeat or paraphrase any of these already-used questions:\n- "
            + "\n- ".join(samples)
            + "\n"
        )

    if effective_difficulty <= 4:
        band = "introductory / scaffolded"
    elif effective_difficulty <= 8:
        band = "standard classroom challenge"
    elif effective_difficulty <= 11:
        band = "advanced multi-step"
    else:
        band = "exam-hard / stretch"

    topic_block = topic_prompt_block(topic)
    if image and topic:
        # Figure constrains the ask, but the curriculum topic lock still applies.
        topic_block = (
            topic_prompt_block(topic)
            + "The provided figure overrides any conflicting visual focus — "
            "ask only about what that figure actually shows, "
            "while remaining inside the topic lock above.\n"
        )

    prompt = (
        f"Generate ONE ORIGINAL {qtype} challenge item for Ghana secondary {label}.\n"
        f"Phase {phase_number}, Level {level_number} of 10 "
        f"(this level has {question_budget} questions — keep the item focused).\n"
        f"Novelty seed: {rng.randint(1, 10_000_000)}.\n"
        f"Hard constraint — curriculum scope (internal only): {scope}\n"
        f"Internal curriculum mapping: {curriculum_tag}. "
        f"Depth target: {target}. Do NOT write SHS/year labels into the question.\n"
        f"{topic_block}"
        f"{image_block}"
        f"Difficulty MUST match {effective_difficulty} on a 1–15 scale ({band}).\n"
        f"Adaptive context: {performance_summary}\n"
        f"{avoid}"
        f"{_bloom_prompt_block(bloom)}"
        "Write ONLY at the cognitive level specified above. "
        "Do not default every item to application or analysis — "
        "Atlas balances recall, understanding, application, and analysis equally.\n"
        "Keep the item necessary and curriculum-focused: one clear learning check, "
        "no filler or vague \"good study habit\" questions.\n"
        f"{_schema_instructions(qtype, has_image=bool(image), labelled=labelled)}"
    )

    try:
        parsed = await _deepseek_json(
            [
                {
                    "role": "system",
                    "content": (
                        "You are Atlas, an adaptive AI assessment designer for Ghana secondary learners. "
                        "Every item must be fully answerable from the text and any provided diagram. "
                        "Follow the requested Bloom cognitive level exactly "
                        "(recall, understanding, application, or analysis). "
                        "Obey the HARD TOPIC LOCK and phase curriculum scope exactly. "
                        "If a figure is provided, the question MUST match that figure exactly — "
                        "never ask about a plane mirror when the figure is a landscape, "
                        "never ask about a pie chart when the figure is something else. "
                        "Never reference missing charts/tables/images. "
        "Never expose SHS, WAEC, WASSCE, Phase, or Year labels. "
                        "Never write meta tags like [Subject · difficulty N]. "
                        "Never ask study-habit or textbook section/chapter/unit navigation "
                        "questions. Reply with JSON only."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.55 if labelled else 0.7,
        )
        if not parsed or not parsed.get("question_text"):
            _dev_log_reject(
                "empty_or_unparsed_llm",
                subject=subject,
                qtype=qtype,
            )
            return None

        text = _sanitize_learner_text(str(parsed["question_text"]).strip())
        if normalize_question_text(text) in exclude_texts:
            _dev_log_reject(
                "duplicate_stem",
                detail=text[:80],
                subject=subject,
                qtype=qtype,
            )
            return None

        resolved_type = _align_type_to_payload(
            qtype,
            str(parsed.get("question_type") or qtype),
            parsed,
        )

        # If model asks for labels but we don't have a labelled asset, re-plan + retrieve
        if (
            subject not in NO_IMAGE_SUBJECTS
            and needs_labelled_diagram({"question_text": text, "question_type": resolved_type})
            and not labelled
        ):
            label_plan = ImagePlanner.plan_from_curriculum_topic(
                topic,
                subject=subject,
                requires_labels=True,
                question_type="diagram_label",
            )
            if not label_plan.concept:
                label_plan.concept = text[:80]
                label_plan.search_keywords = [f"Labelled {label_plan.concept} Diagram"]
            svg = None
            if images_mode == "local_only":
                svg = await retrieve_for_plan_local_only(label_plan)
            elif images_mode == "full":
                svg = await retrieve_for_plan(label_plan)
            # images_mode == "off": leave svg None (no live retrieve)
            if svg and (svg.get("labels") or svg.get("source") == "atlas_svg"):
                image = svg
                labelled = True
                resolved_type = "diagram_label"
                repaired = await _deepseek_json(
                    [
                        {
                            "role": "system",
                            "content": (
                                "Rewrite as a diagram-labelling MCQ for the PROVIDED labelled diagram. "
                                "Ask which letter matches a structure. JSON only."
                            ),
                        },
                        {
                            "role": "user",
                            "content": (
                                f"Labels: {labels_legend_text(image)}\n"
                                f"Topic: {(topic or {}).get('topic')}\n"
                                f"{_schema_instructions('diagram_label', has_image=True, labelled=True)}"
                            ),
                        },
                    ],
                    temperature=0.35,
                )
                if repaired and repaired.get("question_text"):
                    parsed = repaired
                    text = _sanitize_learner_text(str(parsed["question_text"]).strip())
                    resolved_type = "diagram_label"

        # Fake labels on unlabelled stock → repair to whole-diagram question
        if (
            _asks_for_fake_labels(text)
            and image
            and image.get("source") != "atlas_svg"
        ):
            repaired = await _deepseek_json(
                [
                    {
                        "role": "system",
                        "content": (
                            "Rewrite so you do NOT ask about lettered labels. "
                            "Ask what the whole diagram shows. JSON only."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Original: {json.dumps(parsed)}\nImage: {image.get('alt')}\n"
                            f"{_schema_instructions(resolved_type, has_image=True, labelled=False)}"
                        ),
                    },
                ],
                temperature=0.35,
            )
            if repaired and repaired.get("question_text"):
                parsed = repaired
                text = _sanitize_learner_text(str(parsed["question_text"]).strip())

        options, correct = _coerce_options(resolved_type, parsed)
        if not correct:
            _dev_log_reject(
                "empty_correct_answer",
                subject=subject,
                qtype=resolved_type,
            )
            return None

        # Merge stem into fill_blank template when template is too thin
        if resolved_type == "fill_blank":
            template = str(options.get("template") or "")
            if text and text.lower() not in template.lower() and "___" in template:
                options["template"] = f"{text} {template}".strip()
            elif text and "___" not in template:
                options["template"] = f"{text} ___".strip() if "___" not in text else text
            template = str(options.get("template") or "")
            template = re.sub(r"_{3,}", "___", template)
            options["template"] = template
            blanks = len(re.findall(r"___", template))
            answers = list(options.get("answers") or [])
            if blanks and answers and len(answers) != blanks:
                if len(answers) < blanks:
                    answers = answers + [answers[-1]] * (blanks - len(answers))
                else:
                    answers = answers[:blanks]
                options["answers"] = answers
                correct = "|".join(str(a) for a in answers)

        if not _structure_valid(resolved_type, options, correct, text):
            _dev_log_reject(
                "invalid_structure",
                subject=subject,
                qtype=resolved_type,
                detail="choices/items/matches incomplete",
            )
            return None

        legend = None
        concept_for_match = str((topic or {}).get("topic") or plan.concept or "")

        # Validate image against FULL metadata (incl. source) BEFORE learner scrub.
        keep_image = False
        if image and subject not in NO_IMAGE_SUBJECTS:
            match_ok = _image_matches_text(image, text, concept=concept_for_match)
            conflict = _image_question_conflict(image, text)
            if match_ok and not conflict:
                keep_image = True
                legend = _legend_for_image(image, labelled=labelled)
            else:
                _dev_log_reject(
                    "image_mismatch_demote",
                    subject=subject,
                    qtype=resolved_type,
                    detail=f"alt={(image.get('alt') or '')[:60]} match={match_ok} conflict={conflict}",
                )

        payload: dict[str, Any] = {
            "question_text": text,
            "question_type": resolved_type,
            "options": options,
            "correct_answer": correct,
            "explanation": _sanitize_learner_text(str(parsed.get("explanation") or "")),
            "image_query": (topic or {}).get("image_query") if keep_image else None,
            "target_level": target,
            "curriculum_topic": (topic or {}).get("topic"),
            "cognitive_level": bloom,
            "source": "llm",
        }
        if legend:
            opts = dict(payload["options"] or {})
            opts["legend"] = legend
            payload["options"] = opts

        if keep_image:
            # Scrub attribution only AFTER successful validation
            payload = _bind_image(payload, image)
        else:
            # Image failed / missing / banned subject → text question, keep LLM stem
            if image or resolved_type in ("image_mcq", "diagram_label"):
                payload = _demote_to_text_question(
                    payload,
                    reason="image_unavailable_or_mismatch",
                    subject=subject,
                )
            elif subject in NO_IMAGE_SUBJECTS:
                payload = _detach_image(payload)
                if resolved_type in ("image_mcq", "diagram_label"):
                    payload["question_type"] = "mcq"
                payload = _scrub_visual_language(payload)

        # fill_blank that still references missing charts → unusable
        if (
            str(payload.get("question_type")) == "fill_blank"
            and not fill_blank_is_self_contained(payload)
        ):
            _dev_log_reject(
                "incomplete_fill_blank",
                subject=subject,
                qtype="fill_blank",
            )
            return None

        # Orphan visual language without an image → scrub; reject only if still broken
        if visual_without_image(payload):
            payload = _scrub_visual_language(payload)
            if str(payload.get("question_type")) in ("image_mcq", "diagram_label"):
                payload = _demote_to_text_question(
                    payload,
                    reason="visual_language_without_image",
                    subject=subject,
                )
            if visual_without_image(payload):
                _dev_log_reject(
                    "visual_without_image",
                    subject=subject,
                    qtype=str(payload.get("question_type") or ""),
                    detail=str(payload.get("question_text") or "")[:80],
                )
                return None

        final_opts = (
            payload.get("options") if isinstance(payload.get("options"), dict) else {}
        )
        final_type = str(payload.get("question_type") or resolved_type)
        if not _structure_valid(
            final_type,
            final_opts,
            str(payload.get("correct_answer") or ""),
            str(payload.get("question_text") or ""),
        ):
            _dev_log_reject(
                "post_process_structure",
                subject=subject,
                qtype=final_type,
            )
            return None

        # Stage 3 — curriculum alignment (topic lock + no year-label leaks)
        ok_curriculum, curriculum_reason = curriculum_gate(
            payload,
            topic=topic,
            phase_number=phase_number,
            subject=subject,
        )
        if not ok_curriculum:
            _dev_log_reject(
                "off_curriculum",
                subject=subject,
                qtype=final_type,
                detail=curriculum_reason
                or (topic or {}).get("topic", "")[:60],
            )
            return None

        if is_unsafe_learner_question(payload):
            _dev_log_reject(
                "unsafe_filler_or_meta",
                subject=subject,
                qtype=final_type,
                detail=str(payload.get("question_text") or "")[:80],
            )
            return None

        _dev_log_source(
            "llm",
            subject=subject,
            qtype=final_type,
            note=(
                f"bloom={bloom} topic={(topic or {}).get('topic', '-')!s} "
                f"image=" + ("yes" if payload.get("image") else "no")
            ),
        )
        return payload
    except Exception as exc:
        logger.warning("DeepSeek question gen failed: %s", exc)
        _dev_log_reject("exception", subject=subject, detail=str(exc)[:120])
    return None


async def generate_subject_question(
    *,
    phase_number: int,
    level_number: int,
    subject: str,
    effective_difficulty: int,
    performance_summary: str,
    exclude_bank_ids: set[str] | None = None,
    exclude_texts: set[str] | None = None,
    question_budget: int | None = None,
    rng: random.Random | None = None,
    max_attempts: int | None = None,
    forced_type: str | None = None,
) -> dict[str, Any]:
    """LLM-first multi-type generation with quality gates; bank then fallback."""
    rng = rng or random.Random()
    used_ids = exclude_bank_ids or set()
    used_texts = set(exclude_texts or set())
    budget = question_budget if question_budget is not None else 10
    attempts = (
        max_attempts
        if max_attempts is not None
        else max(1, int(getattr(settings, "CHALLENGE_LLM_ATTEMPTS", 2)))
    )
    bank_first = bool(getattr(settings, "CHALLENGE_BANK_FIRST", False))
    try:
        from app.llm.deepseek_client import llm_circuit_open

        if llm_circuit_open():
            bank_first = True
    except Exception:
        pass

    def _from_bank() -> dict[str, Any] | None:
        # Try several bank draws — skip filler/meta/section-style stems.
        for _ in range(6):
            from_bank = select_from_bank(
                phase_number=phase_number,
                subject=subject,
                effective_difficulty=effective_difficulty,
                exclude_ids=used_ids,
                rng=rng,
            )
            if not from_bank:
                return None
            from_bank["source"] = "bank"
            from_bank["question_text"] = _sanitize_learner_text(
                str(from_bank["question_text"])
            )
            opts = from_bank.get("options")
            if isinstance(opts, dict) and "choices" not in opts:
                from_bank["options"] = {"choices": opts, **opts}
            if is_unsafe_learner_question(from_bank):
                bank_id = str(from_bank.get("bank_id") or "")
                if bank_id:
                    used_ids.add(bank_id)
                _dev_log_reject(
                    "unsafe_bank_stem",
                    subject=subject,
                    qtype=str(from_bank.get("question_type") or "mcq"),
                    detail=str(from_bank.get("question_text") or "")[:80],
                )
                continue
            norm = normalize_question_text(from_bank["question_text"])
            if norm in used_texts:
                bank_id = str(from_bank.get("bank_id") or "")
                if bank_id:
                    used_ids.add(bank_id)
                continue
            return from_bank
        return None

    def _safe_fallback(salt: int) -> dict[str, Any]:
        item = _fallback_question(
            subject,
            effective_difficulty,
            salt=salt,
            phase_number=phase_number,
        )
        # Curriculum fallbacks are authored safe; still guard.
        if is_unsafe_learner_question(item):
            raise RuntimeError("curriculum fallback marked unsafe")
        return item

    if bank_first:
        banked = _from_bank()
        if banked:
            _dev_log_source(
                "bank",
                subject=subject,
                qtype=str(banked.get("question_type") or ""),
                note="reason=circuit_or_bank_first",
            )
            return banked

    for attempt_i in range(attempts):
        llm = await _llm_question(
            phase_number=phase_number,
            level_number=level_number,
            subject=subject,
            effective_difficulty=effective_difficulty,
            performance_summary=performance_summary,
            question_budget=budget,
            exclude_texts=used_texts,
            rng=rng,
            forced_type=forced_type,
        )
        if llm:
            if is_unsafe_learner_question(llm):
                _dev_log_reject(
                    "unsafe_filler_or_meta",
                    subject=subject,
                    qtype=str(llm.get("question_type") or ""),
                    detail=str(llm.get("question_text") or "")[:80],
                )
                continue
            return llm
        logger.info(
            "challenge_llm_attempt_failed attempt=%s/%s subject=%s forced_type=%s",
            attempt_i + 1,
            attempts,
            subject,
            forced_type or "-",
        )

    banked = _from_bank()
    if banked:
        _dev_log_source(
            "bank",
            subject=subject,
            qtype=str(banked.get("question_type") or ""),
            note=f"reason=llm_exhausted_after_{attempts}_attempts",
        )
        return banked

    for salt in range(8):
        fallback = _safe_fallback(salt + rng.randint(0, 50))
        if normalize_question_text(fallback["question_text"]) not in used_texts:
            _dev_log_source(
                "fallback",
                subject=subject,
                qtype=str(fallback.get("question_type") or ""),
                note="reason=bank_miss",
            )
            return fallback
    fallback = _safe_fallback(rng.randint(0, 999))
    _dev_log_source(
        "fallback",
        subject=subject,
        qtype=str(fallback.get("question_type") or ""),
        note="reason=last_resort",
    )
    return fallback


def _parse_json(content: str) -> dict[str, Any] | None:
    content = content.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", content, re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                return None
    return None
