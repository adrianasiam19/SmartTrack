"""
Internal Ghana SHS curriculum topic anchors for challenge generation.

Phase mapping (never shown to learners as SHS labels):
  Phase 1 → SHS 1 topics only
  Phase 2 → SHS 2 topics only
  Phase 3 → SHS 3 emphasis, with SHS 1–2 reinforcement

Each topic includes a reliable educational image_query so diagrams can be
resolved BEFORE the question is written (image-first alignment).

Stage 3 also provides post-generation curriculum gates (topic lock + phase scope).
"""
from __future__ import annotations

import random
import re
from typing import Any

_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "and",
        "or",
        "of",
        "to",
        "in",
        "on",
        "for",
        "from",
        "with",
        "as",
        "at",
        "by",
        "is",
        "are",
        "be",
        "its",
        "this",
        "that",
        "these",
        "those",
        "using",
        "shown",
        "simple",
        "overview",
        "basics",
        "written",
        "scenario",
        "diagram",
        "figure",
        "educational",
        "identify",
        "explain",
        "relate",
        "compare",
        "interpret",
        "describe",
        "overall",
        "main",
        "role",
        "type",
        "whole",
        "without",
        "lettered",
        "labels",
        "parts",
        "process",
        "concepts",
        "concept",
        "focus",
        "short",
        "text",
        "facts",
        "given",
        "numbers",
        "quantity",
        "stem",
    }
)

# Learner-facing text must never expose internal year mapping.
_CURRICULUM_LABEL_LEAK_RE = re.compile(
    r"\b("
    r"SHS\s*[123]|"
    r"senior\s*high|"
    r"WASSCE|"
    r"WAEC|"
    r"Phase\s*[123]|"
    r"Year\s*[123]|"
    r"Form\s*[123]|"
    r"textbook\s*chapter|"
    r"syllabus"
    r")\b",
    re.I,
)

# topic, image_query (search), concept_focus (what questions may ask)
CURRICULUM_TOPICS: dict[int, dict[str, list[dict[str, str]]]] = {
    1: {
        "integrated_science": [
            {
                "topic": "Plant and animal cells",
                "image_query": "simple plant cell diagram organelles",
                "focus": "Identify the overall cell type or main visible parts as a whole (cell wall, chloroplast region) without lettered labels.",
            },
            {
                "topic": "Diffusion and osmosis",
                "image_query": "osmosis diagram semi permeable membrane",
                "focus": "Identify the process shown (osmosis/diffusion) and direction of water/particle movement.",
            },
            {
                "topic": "Photosynthesis overview",
                "image_query": "photosynthesis process diagram leaf",
                "focus": "Identify photosynthesis inputs/outputs or that the diagram shows photosynthesis.",
            },
            {
                "topic": "Human digestive system overview",
                "image_query": "human digestive system diagram",
                "focus": "Identify the organ system shown and its overall function.",
            },
            {
                "topic": "Simple electrical circuit",
                "image_query": "simple series circuit diagram battery bulb",
                "focus": "Identify circuit type or role of battery/bulb in the whole circuit.",
            },
            {
                "topic": "States of matter",
                "image_query": "states of matter particle diagram solid liquid gas",
                "focus": "Match particle arrangement to solid, liquid, or gas.",
            },
        ],
        "social_studies": [
            {
                "topic": "Map reading basics",
                "image_query": "",
                "focus": "Explain how to read directions, symbols, or scale on a map using a text scenario.",
            },
            {
                "topic": "Ghana's physical environment",
                "image_query": "",
                "focus": "Describe Ghana's location, neighbours, or key physical features from written facts.",
            },
            {
                "topic": "Environmental sanitation",
                "image_query": "",
                "focus": "Identify pollution/sanitation problems and good community responses from a written scenario.",
            },
        ],
        "core_maths": [
            {
                "topic": "Number line",
                "image_query": "number line integers educational diagram",
                "focus": "Read values or compare positions on a number line.",
            },
            {
                "topic": "Simple bar chart",
                "image_query": "simple bar chart educational graph",
                "focus": "Read the tallest bar or compare categories from the chart.",
            },
            {
                "topic": "Fractions basics",
                "image_query": "",
                "focus": "Compare, simplify, or find a fraction of a quantity from given numbers in the stem.",
            },
            {
                "topic": "Simple percentages",
                "image_query": "",
                "focus": "Find a percentage of a quantity or convert between percent and fraction using numbers in the stem.",
            },
        ],
        "english": [
            {
                "topic": "Reading comprehension",
                "image_query": "",
                "focus": "Infer main idea, mood, or purpose from a short written passage.",
            },
            {
                "topic": "Parts of speech basics",
                "image_query": "",
                "focus": "Identify nouns, verbs, adjectives, or adverbs in a short sentence.",
            },
            {
                "topic": "Simple sentence structure",
                "image_query": "",
                "focus": "Identify subject/predicate or fix a basic sentence-structure error in a short example.",
            },
        ],
    },
    2: {
        "integrated_science": [
            {
                "topic": "Respiratory system",
                "image_query": "human respiratory system lungs diagram",
                "focus": "Identify the system shown and overall gas exchange role.",
            },
            {
                "topic": "Circulatory system / heart",
                "image_query": "human heart external anatomy diagram",
                "focus": "Identify that the diagram shows the heart/circulatory organ and its pumping role.",
            },
            {
                "topic": "Food chains and ecosystems",
                "image_query": "food chain ecosystem diagram producers consumers",
                "focus": "Identify producers/consumers or energy flow direction in the whole web.",
            },
            {
                "topic": "Acids, bases and indicators",
                "image_query": "pH scale diagram acids bases",
                "focus": "Interpret acidic vs basic regions on a pH scale diagram.",
            },
            {
                "topic": "Reflection of light",
                "image_query": "plane mirror reflection ray diagram incident reflected normal",
                "focus": "Use the ray diagram: incident ray, normal, reflected ray, and equal angles.",
            },
            {
                "topic": "Reproduction in flowering plants",
                "image_query": "flower structure diagram petals stigma ovary",
                "focus": "Identify that the diagram shows a flower and relate to reproduction overall.",
            },
        ],
        "social_studies": [
            {
                "topic": "Climate and vegetation",
                "image_query": "",
                "focus": "Relate climate zones to vegetation patterns using written descriptions.",
            },
            {
                "topic": "Population and settlement",
                "image_query": "",
                "focus": "Compare urban and rural settlement features and related social issues from text.",
            },
            {
                "topic": "Natural resources of Ghana",
                "image_query": "",
                "focus": "Explain the economic importance of Ghana's natural resources from a written scenario.",
            },
        ],
        "core_maths": [
            {
                "topic": "Linear graphs",
                "image_query": "linear graph coordinate plane educational",
                "focus": "Read slope/intercept concepts from a straight-line graph.",
            },
            {
                "topic": "Pie charts",
                "image_query": "pie chart educational percentages",
                "focus": "Compare sectors or estimate proportions from the pie chart.",
            },
        ],
        "english": [
            {
                "topic": "Inferring meaning from text",
                "image_query": "",
                "focus": "Infer purpose, audience, or main idea from a short written description or passage.",
            },
        ],
    },
    3: {
        "integrated_science": [
            {
                "topic": "Genetics and inheritance overview",
                "image_query": "Punnett square diagram genetics",
                "focus": "Interpret a Punnett square outcome at a conceptual level.",
            },
            {
                "topic": "Nervous system / neuron",
                "image_query": "neuron structure diagram axon dendrite",
                "focus": "Identify that the diagram shows a neuron and its signalling role.",
            },
            {
                "topic": "Electromagnetic spectrum / waves",
                "image_query": "electromagnetic spectrum diagram",
                "focus": "Identify the spectrum shown and compare wave regions conceptually.",
            },
            {
                "topic": "Organic chemistry functional groups overview",
                "image_query": "hydrocarbon molecule structure diagram",
                "focus": "Identify that a molecular structure diagram is shown and relate to carbon compounds.",
            },
            {
                "topic": "Ecology and pollution (reinforcement)",
                "image_query": "water pollution industrial waste illustration",
                "focus": "Identify the environmental issue and a mitigation strategy.",
            },
            {
                "topic": "Cell division overview (reinforcement)",
                "image_query": "mitosis stages diagram educational",
                "focus": "Identify mitosis as the process shown at a high level.",
            },
        ],
        "social_studies": [
            {
                "topic": "Governance and constitution",
                "image_query": "",
                "focus": "Explain branches of government or democratic participation from written facts.",
            },
            {
                "topic": "Globalisation and development",
                "image_query": "",
                "focus": "Relate trade, interdependence, or development using a written scenario.",
            },
            {
                "topic": "Map skills advanced (reinforcement)",
                "image_query": "",
                "focus": "Interpret map types (e.g. relief/contour concepts) from written descriptions, not a figure.",
            },
        ],
        "core_maths": [
            {
                "topic": "Trigonometry right triangle",
                "image_query": "right triangle trigonometry diagram opposite adjacent",
                "focus": "Identify opposite/adjacent/hypotenuse relationships from the triangle figure.",
            },
            {
                "topic": "Statistics graphs",
                "image_query": "histogram frequency chart educational",
                "focus": "Read distribution shape or modal class conceptually from the chart.",
            },
        ],
        "english": [
            {
                "topic": "Critical reading of persuasive text",
                "image_query": "",
                "focus": "Identify purpose, tone, or intended audience of a short written campaign or notice.",
            },
        ],
    },
}


def phase_curriculum_label(phase_number: int) -> str:
    """Internal depth label for prompts — never shown in learner UI."""
    return {1: "SHS 1", 2: "SHS 2", 3: "SHS 3 (with SHS 1–2 reinforcement)"}.get(
        phase_number, "SHS 1"
    )


def _topics_for_phase_subject(phase_number: int, subject: str) -> list[dict[str, str]]:
    return list(CURRICULUM_TOPICS.get(phase_number, {}).get(subject) or [])


def allowed_topic_pool(
    phase_number: int,
    subject: str,
) -> list[dict[str, str]]:
    """Topics permitted for this phase (Phase 3 includes SHS 1–2 reinforcement)."""
    phase = phase_number if phase_number in CURRICULUM_TOPICS else 1
    pools = _topics_for_phase_subject(phase, subject)
    if phase >= 3:
        for earlier in (1, 2):
            pools.extend(_topics_for_phase_subject(earlier, subject))
    if not pools:
        for topics in CURRICULUM_TOPICS.get(phase, {}).values():
            pools.extend(topics)
    return pools


def pick_curriculum_topic(
    phase_number: int,
    subject: str,
    rng: random.Random | None = None,
) -> dict[str, str] | None:
    """
    Pick one curriculum topic for generation.

    Phase 3: ~65% primary SHS 3 topics, ~35% SHS 1–2 reinforcement
    (still within the allowed Phase 3 scope).
    """
    rng = rng or random.Random()
    phase = phase_number if phase_number in CURRICULUM_TOPICS else 1

    if phase >= 3:
        primary = _topics_for_phase_subject(3, subject)
        earlier: list[dict[str, str]] = []
        for p in (1, 2):
            earlier.extend(_topics_for_phase_subject(p, subject))
        if primary and earlier:
            pool = primary if rng.random() < 0.65 else earlier
        else:
            pool = primary or earlier
    else:
        pool = _topics_for_phase_subject(phase, subject)

    if not pool:
        pool = allowed_topic_pool(phase, subject)
    if not pool:
        return None
    return dict(rng.choice(pool))


def topic_prompt_block(topic: dict[str, str] | None) -> str:
    if not topic:
        return ""
    name = (topic.get("topic") or "").strip()
    focus = (topic.get("focus") or "").strip()
    lines = [
        f"HARD TOPIC LOCK (internal): The item MUST be about exactly this topic: {name}.",
        f"Concept focus (required): {focus}.",
        "Do not switch subject, invent a different lesson, or jump to a later-year topic.",
        "Do not write filler study-habit questions unrelated to this topic.",
        "Learner-facing text must NEVER mention SHS, WAEC, WASSCE, Phase, Year 1/2/3, "
        "Form, syllabus, or textbook chapters.",
    ]
    image_query = (topic.get("image_query") or "").strip()
    if image_query:
        lines.append(f"Preferred diagram search: {image_query}.")
    else:
        lines.append("Do NOT invent or refer to any diagram, map, image, or illustration.")
    return "\n".join(lines) + "\n"


def _tokenize(blob: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", (blob or "").lower()) if t}


def topic_anchor_terms(topic: dict[str, str] | None) -> set[str]:
    """Distinctive content words from topic title + focus for soft alignment checks."""
    if not topic:
        return set()
    raw = f"{topic.get('topic') or ''} {topic.get('focus') or ''}"
    terms: set[str] = set()
    for tok in _tokenize(raw):
        if tok in _STOPWORDS or len(tok) < 4:
            continue
        terms.add(tok)
        # Light plural stemming (avoid mangling -sis / -ss / -us words)
        if (
            tok.endswith("s")
            and not tok.endswith(("ss", "us", "is"))
            and len(tok) > 4
        ):
            terms.add(tok[:-1])
        if tok.endswith("ies") and len(tok) > 5:
            terms.add(tok[:-3] + "y")
    return terms


def _payload_learner_blob(payload: dict[str, Any]) -> str:
    parts: list[str] = [str(payload.get("question_text") or "")]
    expl = str(payload.get("explanation") or "")
    if expl:
        parts.append(expl)
    correct = str(payload.get("correct_answer") or "")
    if correct:
        parts.append(correct)
    opts = payload.get("options") if isinstance(payload.get("options"), dict) else {}
    if opts.get("template"):
        parts.append(str(opts["template"]))
    choices = opts.get("choices")
    if isinstance(choices, dict):
        parts.extend(str(v) for v in choices.values())
    elif isinstance(choices, list):
        parts.extend(str(v) for v in choices)
    for key in ("left", "right", "items", "pairs"):
        val = opts.get(key)
        if isinstance(val, list):
            parts.extend(str(v) for v in val)
        elif isinstance(val, dict):
            parts.extend(str(v) for v in val.values())
    return "\n".join(parts)


def _term_hit_count(blob_tokens: set[str], terms: set[str]) -> int:
    return sum(1 for t in terms if t in blob_tokens)


def _foreign_exclusive_topics(
    phase_number: int,
    subject: str,
    assigned: dict[str, str] | None,
) -> list[dict[str, str]]:
    """Topics allowed only in other phases (used to catch year-level drift)."""
    if phase_number >= 3:
        return []
    allowed_names = {
        (t.get("topic") or "").strip().lower()
        for t in allowed_topic_pool(phase_number, subject)
    }
    assigned_name = ((assigned or {}).get("topic") or "").strip().lower()
    foreign: list[dict[str, str]] = []
    for other_phase, by_subject in CURRICULUM_TOPICS.items():
        if other_phase == phase_number:
            continue
        for t in by_subject.get(subject) or []:
            name = (t.get("topic") or "").strip().lower()
            if not name or name in allowed_names or name == assigned_name:
                continue
            # Skip soft reinforcement-labelled titles that overlap earlier years
            if "reinforcement" in name:
                continue
            foreign.append(t)
    return foreign


def curriculum_gate(
    payload: dict[str, Any],
    *,
    topic: dict[str, str] | None,
    phase_number: int,
    subject: str,
) -> tuple[bool, str]:
    """
    Soft post-generation curriculum enforcement.

    Returns (ok, reason). reason is empty when ok.
    Prefers keeping good paraphrases; rejects clear label leaks and strong year drift.
    """
    blob = _payload_learner_blob(payload)
    if _CURRICULUM_LABEL_LEAK_RE.search(blob):
        return False, "curriculum_label_leak"

    if not topic:
        return True, ""

    # English passages often paraphrase without repeating topic title words.
    if subject == "english":
        return True, ""

    anchors = topic_anchor_terms(topic)
    tokens = _tokenize(blob)
    home_hits = _term_hit_count(tokens, anchors)

    # Strong foreign-topic match with no home-topic signal → wrong year/topic.
    best_foreign = 0
    best_foreign_name = ""
    for foreign in _foreign_exclusive_topics(phase_number, subject, topic):
        f_terms = topic_anchor_terms(foreign)
        # Prefer distinctive multi-word topic titles
        score = _term_hit_count(tokens, f_terms)
        if score > best_foreign:
            best_foreign = score
            best_foreign_name = foreign.get("topic") or ""

    if home_hits == 0 and best_foreign >= 2:
        return False, f"topic_drift:{best_foreign_name[:40]}"

    # Distinctive assigned topic with zero overlap → likely ignored the lock.
    distinctive = {t for t in anchors if len(t) >= 5}
    if home_hits == 0 and len(distinctive) >= 2:
        return False, f"topic_miss:{(topic.get('topic') or '')[:40]}"

    return True, ""
