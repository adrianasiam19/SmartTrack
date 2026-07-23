"""Generate adaptive mixed-format challenge questions.

Primary source: DeepSeek LLM (concept-focused, multi-type).
Images: curriculum topic → resolve diagram FIRST → LLM writes a question
that matches the actual image metadata (image-first alignment).

Internal curriculum depth:
  Phase 1 → SHS 1 only
  Phase 2 → SHS 2 only
  Phase 3 → SHS 3 with SHS 1–2 reinforcement

Learner-facing text must never mention SHS / textbook chapter references.
Labelled-part questions MUST use Atlas SVG diagrams with real A/B/C arrows.
Every fill-blank must be self-contained (all data in the stem/template).
"""
from __future__ import annotations

import json
import logging
import random
import re
from typing import Any

import httpx

from app.config import settings
from app.media.educational_images import (
    mentions_visual,
    resolve_educational_image,
)
from app.media.labelled_diagrams import labels_legend_text, pick_labelled_diagram
from app.phases.academic_bank import select_question as select_from_bank
from app.phases.adaptive import normalize_question_text
from app.phases.curriculum_topics import (
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
        "Do not include SHS 2, SHS 3, or WASSCE-only items."
    ),
    2: (
        "Use ONLY SHS 2 (Year 2) Ghana secondary curriculum topics for this subject. "
        "Do not include SHS 3-only or WASSCE-only items."
    ),
    3: (
        "Primary focus: SHS 3 (Year 3) Ghana secondary topics. "
        "You may reinforce important SHS 1–2 concepts where helpful. "
        "Prefer exam-style application when difficulty is high (10+)."
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
        "mcq": 2,
        "true_false": 2,
        "fill_blank": 1,
        "short_answer": 2,
        "matching": 2,
        "ordering": 2,
        "scenario": 3,
        "image_mcq": 2,
        "diagram_label": 1,
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
        "image_mcq": 1,
        "diagram_label": 0,
    },
}

SHS_LEAK_RE = re.compile(
    r"\b(SHS\s*[123]|senior\s*high|WASSCE\s*past\s*paper|your\s*textbook|"
    r"form\s*[123]|WAEC\s*syllabus)\b",
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


def _pick_question_type(subject: str, rng: random.Random) -> str:
    weights = TYPE_WEIGHTS.get(subject) or TYPE_WEIGHTS["integrated_science"]
    pool: list[str] = []
    for t, w in weights.items():
        pool.extend([t] * max(0, int(w)))
    return rng.choice(pool) if pool else "mcq"


def _fallback_question(subject: str, effective_difficulty: int, salt: int = 0) -> dict[str, Any]:
    label = SUBJECT_LABELS.get(subject, subject)
    variants = [
        "Which approach best shows careful reasoning for this subject?",
        "What is the most reliable next step when solving a problem here?",
        "Which habit most improves accuracy in this subject?",
        "How should a careful student check their work?",
    ]
    return {
        "question_text": (
            f"[{label} · difficulty {effective_difficulty}] "
            f"{variants[salt % len(variants)]}"
        ),
        "question_type": "mcq",
        "options": {
            "choices": {
                "A": "Skip the problem and guess",
                "B": "Break it into steps and check your work",
                "C": "Ignore instructions",
                "D": "Copy a random answer",
            }
        },
        "correct_answer": "B",
        "explanation": "Careful step-by-step reasoning is the reliable approach.",
        "source": "fallback",
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
            "Include left, right, correct_matches (0-based right indices)."
        )
    if qtype == "ordering":
        return (
            f"{common}\n"
            'question_type must be "ordering".\n'
            "Include items in CORRECT order."
        )
    return common


def _sanitize_learner_text(text: str) -> str:
    if not text:
        return text
    cleaned = SHS_LEAK_RE.sub("your studies", text)
    cleaned = re.sub(r"\bSHS\b", "", cleaned, flags=re.I)
    return cleaned.strip()


def _asks_for_fake_labels(text: str) -> bool:
    return bool(FAKE_LABEL_RE.search(text or ""))


def _coerce_options(qtype: str, parsed: dict[str, Any]) -> tuple[dict[str, Any], str]:
    correct = str(parsed.get("correct_answer") or "").strip()
    options: dict[str, Any] = {}

    if qtype in ("mcq", "scenario", "image_mcq", "diagram_label"):
        choices = parsed.get("choices") or parsed.get("options") or {}
        if isinstance(choices, list):
            choices = {chr(65 + i): str(o) for i, o in enumerate(choices[:4])}
        letter_choices: dict[str, str] = {}
        if isinstance(choices, dict):
            letter_choices = {
                str(k).upper()[:1]: _sanitize_learner_text(str(v))
                for k, v in choices.items()
                if str(k).upper()[:1] in "ABCD"
            }
            options = {"choices": letter_choices, **letter_choices}
        if not correct and letter_choices:
            correct = "A"
        correct = correct.upper()[:1]

    elif qtype == "true_false":
        options = {"choices": {"A": "True", "B": "False"}}
        c = correct.lower()
        correct = "true" if c in ("a", "true", "t", "yes") else "false"

    elif qtype == "fill_blank":
        answers = parsed.get("answers") or []
        if not isinstance(answers, list):
            answers = [str(answers)]
        answers = [str(a).strip() for a in answers]
        options = {
            "template": _sanitize_learner_text(
                str(parsed.get("template") or parsed.get("question_text") or "")
            ),
            "answers": answers,
            "hints": [str(h) for h in (parsed.get("hints") or [])][:3],
        }
        correct = "|".join(answers)

    elif qtype == "short_answer":
        accepted = parsed.get("accepted") or parsed.get("accepted_answers") or []
        if not isinstance(accepted, list):
            accepted = [str(accepted)]
        options = {"accepted": [str(a).strip() for a in accepted if str(a).strip()]}
        correct = correct or (options["accepted"][0] if options["accepted"] else "")

    elif qtype == "matching":
        left = [str(x) for x in (parsed.get("left") or [])][:5]
        right = [str(x) for x in (parsed.get("right") or [])][:5]
        matches = parsed.get("correct_matches") or []
        if not isinstance(matches, list):
            matches = []
        matches = [int(m) for m in matches][: len(left)]
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
        items = [str(x) for x in (parsed.get("items") or parsed.get("correct_order") or [])][:6]
        options = {"items": items, "correct_order": items}
        correct = json.dumps(items)

    else:
        choices = parsed.get("options") or parsed.get("choices") or {}
        if isinstance(choices, dict):
            options = {"choices": choices, **choices}
        correct = correct.upper()[:1] if correct else "A"

    return options, correct[:480]


def _bind_image(payload: dict[str, Any], image: dict[str, Any] | None) -> dict[str, Any]:
    if not image:
        return payload
    opts = dict(payload.get("options") or {})
    opts["image"] = image
    payload["options"] = opts
    payload["image"] = image
    return payload


def _strip_diagram_language(text: str) -> str:
    text = re.sub(
        r"(?i)\b(study|look at|observe|examine)\s+the\s+(diagram|figure|image|picture|map|graph)\s*(below|above|shown)?[,:]?\s*",
        "",
        text,
    )
    text = re.sub(r"(?i)\bthe\s+(diagram|figure|image)\s+shows\s+", "Regarding this concept: ", text)
    return text.strip()


async def _deepseek_json(messages: list[dict[str, str]], *, temperature: float = 0.75) -> dict[str, Any] | None:
    async with httpx.AsyncClient(timeout=55.0) as client:
        res = await client.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}"},
            json={
                "model": settings.DEEPSEEK_MODEL,
                "messages": messages,
                "temperature": temperature,
            },
        )
        if res.status_code != 200:
            logger.warning("DeepSeek question gen HTTP %s", res.status_code)
            return None
        content = res.json()["choices"][0]["message"]["content"]
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

    label = SUBJECT_LABELS.get(subject, subject)
    scope = PHASE_SCOPE.get(phase_number, PHASE_SCOPE[1])
    target = _pick_target_level(phase_number, effective_difficulty, rng)
    curriculum_tag = phase_curriculum_label(phase_number)
    qtype = forced_type or _pick_question_type(subject, rng)
    topic = pick_curriculum_topic(phase_number, subject, rng)
    topic_blob = f"{(topic or {}).get('topic','')} {(topic or {}).get('image_query','')} {subject}"

    # Prefer Atlas labelled SVG whenever the type is diagram_label
    labelled = False
    image: dict[str, Any] | None = None
    if qtype == "diagram_label" or (
        subject == "integrated_science" and qtype == "image_mcq" and rng.random() < 0.45
    ):
        image = pick_labelled_diagram(topic_blob, subject)
        labelled = bool(image)
        if labelled:
            qtype = "diagram_label"

    wants_image = labelled or qtype in ("image_mcq", "diagram_label") or (
        subject in ("integrated_science", "social_studies") and rng.random() < 0.3
    )

    image_block = ""
    if wants_image and not image and topic:
        image = await resolve_educational_image(
            topic.get("image_query") or topic.get("topic") or label,
            preferred_alt=topic.get("topic"),
        )
        if not image:
            wants_image = False
            if qtype in ("image_mcq", "diagram_label"):
                qtype = "mcq"

    if image:
        image_block = (
            "An educational diagram is PROVIDED with this item. Write the question for it.\n"
            f"- Image title/alt: {image.get('alt')}\n"
            f"- Source: {image.get('source')}\n"
            f"- Attribution: {image.get('attribution')}\n"
        )
        if labelled and image.get("labels"):
            image_block += (
                f"- Label key: {labels_legend_text(image)}\n"
                "You MUST ask which letter (A/B/C/D) matches a structure from that key.\n"
                "correct_answer must be the letter. choices should be the structure names or letters.\n"
            )
        else:
            image_block += (
                f"- Curriculum topic: {(topic or {}).get('topic')}\n"
                f"- Focus: {(topic or {}).get('focus')}\n"
                "Do NOT ask about lettered labels on this unlabelled figure.\n"
            )
        if qtype == "fill_blank":
            # Visual + fill blank is fragile; prefer MCQ/image types with images
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

    prompt = (
        f"Generate ONE ORIGINAL {qtype} challenge item for Ghana secondary {label}.\n"
        f"Phase {phase_number}, Level {level_number} of 10 "
        f"(this level has {question_budget} questions — keep the item focused).\n"
        f"Novelty seed: {rng.randint(1, 10_000_000)}.\n"
        f"Hard constraint — curriculum scope (internal only): {scope}\n"
        f"Internal curriculum mapping: {curriculum_tag}. "
        f"Depth target: {target}. Do NOT write SHS/year labels into the question.\n"
        f"{topic_prompt_block(topic)}"
        f"{image_block}"
        f"Difficulty MUST match {effective_difficulty} on a 1–15 scale ({band}).\n"
        f"Adaptive context: {performance_summary}\n"
        f"{avoid}"
        "Prioritise conceptual understanding, critical thinking, problem solving, "
        "or real-world application — not rote memorisation.\n"
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
                        "Never reference missing charts/tables/images. "
                        "Never expose SHS labels. Reply with JSON only."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.55 if labelled else 0.7,
        )
        if not parsed or not parsed.get("question_text"):
            return None

        text = _sanitize_learner_text(str(parsed["question_text"]).strip())
        if normalize_question_text(text) in exclude_texts:
            return None

        resolved_type = normalize_question_type(
            str(parsed.get("question_type") or qtype),
            fallback=qtype,
        )

        # If model asks for labels but we only have a stock image, swap to Atlas SVG
        if needs_labelled_diagram({"question_text": text, "question_type": resolved_type}) and not labelled:
            svg = pick_labelled_diagram(f"{text} {topic_blob}", subject)
            if svg:
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
            return None

        # Merge stem into fill_blank template when template is too thin
        if resolved_type == "fill_blank":
            template = str(options.get("template") or "")
            if text and text.lower() not in template.lower() and "___" in template:
                options["template"] = f"{text} {template}".strip()
            elif text and "___" not in template:
                options["template"] = f"{text} ___".strip() if "___" not in text else text

        legend = None
        if image:
            if labelled and image.get("labels"):
                legend = {
                    "title": "Diagram labels",
                    "hint": labels_legend_text(image),
                }
            elif topic:
                legend = {
                    "title": "What to look for",
                    "hint": topic.get("focus") or "",
                }

        payload: dict[str, Any] = {
            "question_text": text,
            "question_type": resolved_type,
            "options": options,
            "correct_answer": correct,
            "explanation": _sanitize_learner_text(str(parsed.get("explanation") or "")),
            "image_query": (topic or {}).get("image_query") if image else None,
            "target_level": target,
            "curriculum_topic": (topic or {}).get("topic"),
            "source": "llm",
        }
        if legend:
            opts = dict(payload["options"] or {})
            opts["legend"] = legend
            payload["options"] = opts

        payload = _bind_image(payload, image)

        # Hard quality gates — reject broken items so caller retries
        if resolved_type == "fill_blank" and not fill_blank_is_self_contained(payload):
            logger.info("Rejected incomplete fill_blank")
            return None
        if visual_without_image(payload):
            # Last chance: attach labelled or stock image, else strip language
            rescue = pick_labelled_diagram(f"{text} {topic_blob}", subject)
            if not rescue and topic:
                rescue = await resolve_educational_image(
                    topic.get("image_query") or topic.get("topic") or "educational diagram",
                    preferred_alt=topic.get("topic"),
                )
            if rescue:
                payload = _bind_image(payload, rescue)
                if rescue.get("source") == "atlas_svg":
                    opts = dict(payload.get("options") or {})
                    opts["legend"] = {
                        "title": "Diagram labels",
                        "hint": labels_legend_text(rescue),
                    }
                    payload["options"] = opts
            else:
                payload["question_text"] = _strip_diagram_language(text)
                opts = payload.get("options") if isinstance(payload.get("options"), dict) else {}
                if opts.get("template"):
                    opts["template"] = _strip_diagram_language(str(opts["template"]))
                if visual_without_image(payload):
                    return None

        return payload
    except Exception as exc:
        logger.warning("DeepSeek question gen failed: %s", exc)
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
    max_attempts: int = 4,
) -> dict[str, Any]:
    """LLM-first multi-type generation with quality gates; bank then fallback."""
    rng = rng or random.Random()
    used_ids = exclude_bank_ids or set()
    used_texts = set(exclude_texts or set())
    budget = question_budget if question_budget is not None else 10

    for _attempt in range(max_attempts):
        llm = await _llm_question(
            phase_number=phase_number,
            level_number=level_number,
            subject=subject,
            effective_difficulty=effective_difficulty,
            performance_summary=performance_summary,
            question_budget=budget,
            exclude_texts=used_texts,
            rng=rng,
        )
        if llm:
            return llm

    from_bank = select_from_bank(
        phase_number=phase_number,
        subject=subject,
        effective_difficulty=effective_difficulty,
        exclude_ids=used_ids,
        rng=rng,
    )
    if from_bank:
        norm = normalize_question_text(from_bank["question_text"])
        if norm not in used_texts:
            from_bank["source"] = "bank"
            from_bank["question_text"] = _sanitize_learner_text(str(from_bank["question_text"]))
            opts = from_bank.get("options")
            if isinstance(opts, dict) and "choices" not in opts:
                from_bank["options"] = {"choices": opts, **opts}
            return from_bank

    for salt in range(8):
        fallback = _fallback_question(subject, effective_difficulty, salt=salt + rng.randint(0, 50))
        if normalize_question_text(fallback["question_text"]) not in used_texts:
            return fallback
    return _fallback_question(subject, effective_difficulty, salt=rng.randint(0, 999))


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
