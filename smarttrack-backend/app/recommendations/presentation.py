"""
Learner-facing recommendation presentation helpers.

Keeps cut-off / ML internals out of the UI copy while reusing existing catalogue data.
"""
from __future__ import annotations

import re
from typing import Any

from app.recommendations.cutoffs import FAMILY_ALIASES, load_knust_cutoffs

# How close cut-offs should sit to the learner aggregate for "Recommended".
NEARBY_RANGE = 2
# How much more competitive (lower cut-off) for the Competitive section.
COMPETITIVE_RANGE = 3
MIN_PROFILE_FIT = 45

TRAIT_PHRASES: dict[str, str] = {
    "analytical": "analytical thinking",
    "analysis": "analytical thinking",
    "problem_solving": "problem-solving ability",
    "problem-solving": "problem-solving ability",
    "curiosity": "curiosity",
    "study_habits": "good study habits",
    "study-habits": "good study habits",
    "persistence": "persistence",
    "leadership": "leadership",
    "empathy": "empathy",
    "creativity": "creativity",
    "creative": "creativity",
    "communication": "communication skills",
    "teamwork": "teamwork",
    "practical": "practical skills",
    "carefulness": "careful attention to detail",
    "social": "working well with others",
    "motivation": "strong motivation",
    "confidence": "confidence",
    "time_management": "time management",
}

# Affinity / internal keys that must never appear as programme names in the UI.
INTERNAL_PROGRAMME_KEYS = {
    "business_law",
    "business law",
    "medicine_health",
    "medicine health",
    "arts_media",
    "arts media",
    "natural_sciences",
    "natural sciences",
    "engineering",
    "computing",
    "computing_it",
    "education",
    "general science",
    "business studies",
}

FAMILY_OVERVIEW: dict[str, dict[str, str]] = {
    "Health Sciences": {
        "overview": (
            "Health-related degree programmes that prepare you for clinical, "
            "laboratory, or community health careers."
        ),
        "skills": "Biology, chemistry, careful observation, empathy, and steady study habits.",
        "careers": "Clinical practice, laboratory science, pharmacy, nursing, public health, and allied health roles.",
    },
    "Engineering": {
        "overview": (
            "Engineering programmes that combine mathematics, physics, and design "
            "to solve real-world technical problems."
        ),
        "skills": "Mathematics, physics, logical thinking, and hands-on problem solving.",
        "careers": "Design, manufacturing, infrastructure, energy, computing hardware, and technical consultancy.",
    },
    "Science": {
        "overview": (
            "Science programmes focused on discovery, analysis, and applied scientific methods "
            "across physical, life, and computational fields."
        ),
        "skills": "Scientific reasoning, mathematics, experimentation, and clear analysis.",
        "careers": "Research, data and computing roles, laboratory work, environmental science, and further professional study.",
    },
    "Natural Sciences": {
        "overview": (
            "Science programmes focused on discovery, analysis, and applied scientific methods "
            "across physical, life, and computational fields."
        ),
        "skills": "Scientific reasoning, mathematics, experimentation, and clear analysis.",
        "careers": "Research, data and computing roles, laboratory work, environmental science, and further professional study.",
    },
}


def humanize_trait_key(raw: str) -> str | None:
    key = re.sub(r"[\s\-]+", "_", str(raw or "").strip().lower())
    if not key or key in INTERNAL_PROGRAMME_KEYS:
        return None
    if key in TRAIT_PHRASES:
        return TRAIT_PHRASES[key]
    # Skip snake_case affinity / technical tags
    if "_" in key and key not in TRAIT_PHRASES:
        nice = TRAIT_PHRASES.get(key.replace("_", " "))
        if nice:
            return nice
        # Convert unknown soft traits carefully
        if any(ch.isdigit() for ch in key):
            return None
        words = key.replace("_", " ").strip()
        if len(words) < 3 or len(words) > 40:
            return None
        if words in INTERNAL_PROGRAMME_KEYS:
            return None
        return words
    return None


def build_psychometric_prose(trait_scores: dict[str, float], limit: int = 5) -> str:
    ranked = sorted(trait_scores.items(), key=lambda x: x[1], reverse=True)
    phrases: list[str] = []
    for tag, _ in ranked:
        phrase = humanize_trait_key(tag)
        if phrase and phrase not in phrases:
            phrases.append(phrase)
        if len(phrases) >= limit:
            break
    if not phrases:
        return (
            "You are building a clearer picture of how you learn, solve problems, "
            "and approach challenges."
        )
    if len(phrases) == 1:
        return f"You demonstrated {phrases[0]}."
    if len(phrases) == 2:
        return f"You demonstrated {phrases[0]} and {phrases[1]}."
    return (
        "You demonstrated "
        + ", ".join(phrases[:-1])
        + f", and {phrases[-1]}."
    )


def is_internal_programme_label(name: str) -> bool:
    return str(name or "").strip().lower() in INTERNAL_PROGRAMME_KEYS


def enrich_programme(item: dict[str, Any], *, why: str, method: str) -> dict[str, Any]:
    family = str(item.get("family") or "")
    meta = FAMILY_OVERVIEW.get(family) or FAMILY_OVERVIEW.get(
        FAMILY_ALIASES.get(family, family), {}
    )
    return {
        "programme": item.get("programme"),
        "family": family,
        "cutoff": item.get("cutoff"),
        "demand": item.get("demand"),
        "aggregate": item.get("aggregate"),
        "headroom": item.get("headroom"),
        "eligibility_band": item.get("eligibility_band"),
        "overview": meta.get(
            "overview",
            "A university degree programme matched to your learning profile and results.",
        ),
        "required_skills": meta.get(
            "skills",
            "Strong subject foundations, focus, and consistent practice.",
        ),
        "career_opportunities": meta.get(
            "careers",
            "Related professional and further-study pathways in this field.",
        ),
        "why_recommended": why,
        "admission_insight": _admission_insight(item),
        "method": method,
        "learn_more_url": None,
    }


def _admission_insight(item: dict[str, Any]) -> str:
    cutoff = item.get("cutoff")
    aggregate = item.get("aggregate")
    band = item.get("eligibility_band")
    if aggregate is None or cutoff is None:
        return "Upload complete results so Atlas can refine admission insights for this programme."
    if band == "eligible" or (isinstance(aggregate, int) and aggregate <= int(cutoff)):
        return (
            f"With an estimated aggregate of {aggregate}, this programme sits near your "
            f"current results band (typical entry around {cutoff})."
        )
    return (
        f"This programme is typically more competitive (entry around {cutoff}) than your "
        f"current estimated aggregate of {aggregate}."
    )


def select_suitable_and_competitive(
    *,
    grades: list[dict[str, str]] | None = None,
    family_fit_scores: dict[str, int] | None = None,
    aggregate: int | None = None,
    catalogue_items: list[dict[str, Any]] | None = None,
    nearby_range: int = NEARBY_RANGE,
    competitive_range: int = COMPETITIVE_RANGE,
    limit: int = 8,
) -> dict[str, Any]:
    """
    Profile-first selection, then aggregate-neighbour filters.

    Suitable: strong profile fit AND cutoff in [aggregate, aggregate + nearby_range]
    Competitive: strong profile fit AND cutoff in [aggregate - competitive_range, aggregate)
    """
    from app.recommendations.cutoffs import apply_cutoff_boundaries

    family_fit_scores = family_fit_scores or {}
    if catalogue_items is None:
        gated = apply_cutoff_boundaries(
            grades=grades or [],
            family_fit_scores=family_fit_scores,
            limit_per_band=50,
        )
        aggregate = (gated.get("aggregate") or {}).get("aggregate")
        catalogue_items = []
        for band_name, rows in (gated.get("bands") or {}).items():
            for row in rows or []:
                item = dict(row)
                item["eligibility_band"] = band_name
                catalogue_items.append(item)
        aggregate_info = gated.get("aggregate")
    else:
        aggregate_info = {"aggregate": aggregate, "complete": aggregate is not None}

    if aggregate is None:
        return {
            "aggregate": aggregate_info,
            "suitable": [],
            "competitive": [],
            "profile_summary": "",
        }

    scored: list[dict[str, Any]] = []
    for item in catalogue_items:
        family = str(item.get("family") or "")
        atlas_family = FAMILY_ALIASES.get(family, family)
        fit = int(
            item.get("family_fit_score")
            or family_fit_scores.get(atlas_family)
            or family_fit_scores.get(family)
            or 50
        )
        row = dict(item)
        row["family_fit_score"] = fit
        scored.append(row)

    scored.sort(
        key=lambda r: (-int(r.get("family_fit_score") or 0), int(r.get("cutoff") or 99))
    )

    suitable: list[dict[str, Any]] = []
    competitive: list[dict[str, Any]] = []

    for row in scored:
        cutoff = int(row.get("cutoff") or 99)
        fit = int(row.get("family_fit_score") or 0)
        if fit < MIN_PROFILE_FIT and len(suitable) >= 3:
            # Still allow top profile matches even if slightly below threshold early on
            continue

        why = (
            f"Atlas matched this programme to your strengths in {row.get('family')} "
            f"using your psychometric profile, challenge performance, and academic results."
        )

        if aggregate <= cutoff <= aggregate + nearby_range:
            suitable.append(
                enrich_programme(row, why=why, method="profile_and_aggregate")
            )
        elif aggregate - competitive_range <= cutoff < aggregate:
            competitive.append(
                enrich_programme(
                    row,
                    why=(
                        why
                        + " It is slightly more competitive than your current aggregate, "
                        "so it appears under Competitive Programmes."
                    ),
                    method="profile_competitive",
                )
            )

    # Ensure we always prefer higher profile fit within each list
    suitable = suitable[:limit]
    competitive = competitive[:limit]

    return {
        "aggregate": aggregate_info,
        "suitable": suitable,
        "competitive": competitive,
    }


def format_ml_as_learner_programmes(
    predictions: list[dict[str, Any]],
    *,
    aggregate: int | None,
) -> list[dict[str, Any]]:
    """Convert ML alternate predictions into the same card shape (no raw confidence)."""
    out: list[dict[str, Any]] = []
    for pred in predictions or []:
        name = str(pred.get("programme") or "")
        if not name or is_internal_programme_label(name):
            continue
        item = {
            "programme": name,
            "family": pred.get("family"),
            "cutoff": pred.get("cutoff"),
            "demand": pred.get("demand"),
            "aggregate": aggregate if aggregate is not None else pred.get("aggregate"),
            "headroom": pred.get("headroom"),
            "eligibility_band": pred.get("eligibility_band"),
            "family_fit_score": int(round(float(pred.get("confidence") or 0) * 100)),
        }
        why = (
            f"Atlas matched {name} to your subject pattern, challenge performance, "
            f"and psychometric profile."
        )
        out.append(enrich_programme(item, why=why, method="ml_decision_tree"))
    return out


def sanitize_phase_suggestions(raw: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """Drop internal affinity labels from stored history for safe display."""
    cleaned: list[dict[str, Any]] = []
    for item in raw or []:
        name = str(item.get("programme") or "")
        if not name or is_internal_programme_label(name):
            continue
        # Skip bare affinity-looking titles
        if re.fullmatch(r"[A-Za-z]+(\s+[A-Za-z]+)?", name) and "BSc" not in name and "B." not in name:
            if name.lower() in INTERNAL_PROGRAMME_KEYS or "_" in str(item.get("key") or ""):
                continue
        card = dict(item)
        card.pop("score", None)
        cleaned.append(card)
    return cleaned
