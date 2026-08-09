"""Stage 1 — Educational content analysis for visual aids.

Decides WHETHER a lesson or challenge should use an educational image,
before any image planning, retrieval, or image-aware generation.

The LLM never fetches images here. It only returns a structured decision.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

# Subjects that almost never benefit from free-search diagrams.
TEXT_HEAVY_SUBJECTS = frozenset(
    {
        "english",
        "english_language",
        "english language",
    }
)

# Strong positive cues: topic usually benefits from a visual.
VISUAL_POSITIVE_RE = re.compile(
    r"(?i)\b("
    r"cell|organelle|nucleus|mitochondria|chloroplast|digestive|heart|lung|"
    r"neuron|brain|anatomy|microscope|apparatus|beaker|bunsen|circuit|"
    r"resistor|osmosis|diffusion|photosynthesis|respiration|flower|leaf|"
    r"plant\s+cell|animal\s+cell|mirror|ray\s+diagram|lens|refraction|"
    r"reflection|magnet|electromagnet|force\s+diagram|vector\s+diagram|"
    r"map|continent|climate|rainfall|population\s+pyramid|graph|chart|"
    r"histogram|pie\s+chart|bar\s+chart|number\s+line|coordinate|"
    r"geometry|triangle|circle\s+theorem|labelled|labeled|diagram|"
    r"pollution|environment|ecosystem|food\s+chain|food\s+web|"
    r"periodic\s+table|atomic|molecule|bonding|laboratory|"
    r"geography|settlement|urban|mining|erosion"
    r")\b"
)

# Strong negative cues: text-only is better.
VISUAL_NEGATIVE_RE = re.compile(
    r"(?i)\b("
    r"grammar|vocabulary|spelling|punctuation|essay|comprehension|"
    r"synonym|antonym|idiom|figure\s+of\s+speech|literary\s+device|"
    r"definition\s+only|define\s+the\s+term|solve\s+for\s+x|"
    r"algebraic\s+expression|expand\s+and\s+simplify|factorise|factorize|"
    r"quadratic\s+equation|simultaneous\s+equation|word\s+problem|"
    r"mental\s+maths|arithmetic|percentages?\s+calculation|"
    r"essay\s+writing|letter\s+writing|summary\s+writing"
    r")\b"
)


@dataclass
class VisualNeedDecision:
    """Result of educational content analysis (Stage 1)."""

    needed: bool
    reason: str = ""
    subject: str = ""
    topic_hint: str = ""
    source: str = "rules"  # rules | llm

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _subject_key(subject: str) -> str:
    return re.sub(r"\s+", " ", (subject or "").strip().lower().replace("_", " "))


def analyze_visual_need_rules(
    *,
    subject: str,
    title: str = "",
    context: str = "",
    question_type: str = "",
) -> VisualNeedDecision:
    """
    Fast deterministic gate used as primary fallback (and offline mode).

    Returns needed=False for text-heavy English / pure algebra / grammar, etc.
    """
    subj = _subject_key(subject)
    blob = f"{title} {context} {question_type}".strip()
    qtype = (question_type or "").lower()

    if subj in TEXT_HEAVY_SUBJECTS or subj.startswith("english"):
        # Rare English exception: illustrated comprehension scenes are out of scope
        # for Stage 1 free-search quality — keep English text-only.
        return VisualNeedDecision(
            needed=False,
            reason="English Language topics are taught as text-only content.",
            subject=subject,
            topic_hint=title.strip(),
            source="rules",
        )

    if qtype in ("diagram_label", "image_mcq"):
        return VisualNeedDecision(
            needed=True,
            reason=f"Question type '{qtype}' requires a visual.",
            subject=subject,
            topic_hint=title.strip(),
            source="rules",
        )

    if VISUAL_NEGATIVE_RE.search(blob) and not VISUAL_POSITIVE_RE.search(blob):
        return VisualNeedDecision(
            needed=False,
            reason="Topic is primarily textual, computational, or definitional.",
            subject=subject,
            topic_hint=title.strip(),
            source="rules",
        )

    if VISUAL_POSITIVE_RE.search(blob):
        return VisualNeedDecision(
            needed=True,
            reason="Topic matches visual-friendly educational concepts "
            "(diagrams, maps, charts, apparatus, or labelled structures).",
            subject=subject,
            topic_hint=title.strip(),
            source="rules",
        )

    # Subject-level defaults when cues are weak
    if any(
        s in subj
        for s in (
            "biology",
            "physics",
            "chemistry",
            "integrated science",
            "geography",
            "social studies",
        )
    ):
        # Social Studies / science: prefer visual when topic is ambiguous but
        # subject typically benefits — still skip pure essay-style cues above.
        return VisualNeedDecision(
            needed=True,
            reason=f"{subject} topics often benefit from a diagram, map, or illustration.",
            subject=subject,
            topic_hint=title.strip(),
            source="rules",
        )

    if "math" in subj:
        # Maths: only when geometry/graph cues already matched positive RE.
        return VisualNeedDecision(
            needed=False,
            reason="Mathematics topic appears computational rather than diagrammatic.",
            subject=subject,
            topic_hint=title.strip(),
            source="rules",
        )

    return VisualNeedDecision(
        needed=False,
        reason="No clear visual need detected; prefer a high-quality text explanation.",
        subject=subject,
        topic_hint=title.strip(),
        source="rules",
    )


async def analyze_visual_need(
    *,
    subject: str,
    title: str = "",
    context: str = "",
    question_type: str = "",
    use_llm: bool = True,
) -> VisualNeedDecision:
    """
    Decide whether an educational visual should be used for this topic.

    Prefer LLM judgement when available; always fall back to rules so lesson
    / challenge generation never blocks.
    """
    rules = analyze_visual_need_rules(
        subject=subject,
        title=title,
        context=context,
        question_type=question_type,
    )

    # Hard gate: English stays text-only regardless of LLM.
    if not rules.needed and (
        _subject_key(subject) in TEXT_HEAVY_SUBJECTS
        or _subject_key(subject).startswith("english")
    ):
        return rules

    if not use_llm or not (getattr(settings, "DEEPSEEK_API_KEY", "") or "").strip():
        return rules

    from app.llm.deepseek_client import deepseek_message_content, llm_circuit_open

    if llm_circuit_open():
        return rules

    prompt = (
        "You are Atlas Educational Content Analyst.\n"
        "Decide whether this SHS learning topic SHOULD use an educational visual aid.\n"
        "Visuals HELP for: biology structures, physics circuits/optics, chemistry apparatus, "
        "geography/maps, social studies scenes (pollution, settlements), labelled maths diagrams, "
        "charts/graphs, laboratory equipment, cells, digestive system, environmental scenes.\n"
        "Visuals do NOT help for: grammar, vocabulary, essay writing, pure algebraic calculations, "
        "definitions without structures, abstract verbal reasoning.\n"
        "Do NOT invent image URLs. Do NOT plan search queries yet.\n"
        "Return ONLY JSON:\n"
        '{"needed": true|false, "reason": "short explanation", "topic_hint": "short concept name"}\n\n'
        f"Subject: {subject}\n"
        f"Title: {title or '(none)'}\n"
        f"Question type: {question_type or 'n/a'}\n"
        f"Context:\n{(context or '')[:1800]}\n"
    )
    try:
        content = await deepseek_message_content(
            [
                {
                    "role": "system",
                    "content": (
                        "Analyse whether a visual aid is educationally useful. "
                        "JSON only. No URLs."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            read_timeout=12.0,
            purpose="visual_need",
        )
        if not content:
            return rules
        parsed = _parse_json(content)
        if not parsed or "needed" not in parsed:
            return rules
        return VisualNeedDecision(
            needed=bool(parsed.get("needed")),
            reason=str(parsed.get("reason") or rules.reason)[:240],
            subject=subject,
            topic_hint=str(parsed.get("topic_hint") or title or rules.topic_hint)[:120],
            source="llm",
        )
    except Exception as exc:
        logger.info("Visual-need LLM fallback to rules: %s", exc)
        return rules


def _parse_json(content: str) -> dict[str, Any] | None:
    content = (content or "").strip()
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
