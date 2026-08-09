"""
BehaviouralProgrammeMatch (BPM) — rank KNUST programmes without WASSCE.

Used after each phase completes. WASSCE/admission cut-offs are a separate
optional refinement path once the learner uploads results.
"""
from __future__ import annotations

from typing import Any

from app.recommendations.cutoffs import FAMILY_ALIASES, load_knust_cutoffs
from app.recommendations.presentation import enrich_programme

# Weights from product design (deterministic, not learned).
W_PSYCH = 0.40
W_CHALLENGE = 0.35
W_LEARNING = 0.15
W_TRAITS = 0.10

FAMILIES = ("Engineering", "Health Sciences", "Natural Sciences")

# Challenge subject keys → families that benefit from that skill signal.
SUBJECT_TO_FAMILIES: dict[str, tuple[str, ...]] = {
    "core_maths": ("Engineering", "Natural Sciences"),
    "math": ("Engineering", "Natural Sciences"),
    "logic": ("Engineering", "Natural Sciences"),
    "integrated_science": ("Natural Sciences", "Health Sciences", "Engineering"),
    "science": ("Natural Sciences", "Health Sciences", "Engineering"),
    "biology": ("Health Sciences", "Natural Sciences"),
    "chemistry": ("Health Sciences", "Natural Sciences", "Engineering"),
    "physics": ("Engineering", "Natural Sciences"),
    "english": ("Natural Sciences",),
    "social_studies": ("Health Sciences",),
    "ict": ("Engineering", "Natural Sciences"),
    "computing": ("Engineering", "Natural Sciences"),
}

# Programme name keywords → bonus when learner is strong in related subjects.
PROGRAMME_SUBJECT_HINTS: list[tuple[tuple[str, ...], tuple[str, ...]]] = [
    (("computer", "comput"), ("core_maths", "math", "logic", "ict", "computing")),
    (("electrical", "eletr"), ("core_maths", "physics", "integrated_science")),
    (("biomed", "biomedic"), ("biology", "chemistry", "integrated_science", "core_maths")),
    (("medic", "nurs", "pharm", "dental", "physio", "midwif"), ("biology", "chemistry", "integrated_science")),
    (("civil", "mechanic", "chemical", "petroleum", "aerospace"), ("core_maths", "physics", "integrated_science")),
    (("stat", "actuar", "math"), ("core_maths", "math", "logic")),
    (("biochem", "biolog", "chemist", "environ"), ("integrated_science", "biology", "chemistry")),
]


def _neutral_families() -> dict[str, float]:
    return {f: 50.0 for f in FAMILIES}


def _max_normalize(raw: dict[str, float]) -> dict[str, int]:
    if not raw:
        return {f: 50 for f in FAMILIES}
    max_s = max(raw.values()) or 1.0
    if max_s <= 0:
        max_s = 1.0
    out = {f: int(round((raw.get(f, 0.0) / max_s) * 100)) for f in FAMILIES}
    for f in FAMILIES:
        out.setdefault(f, 50)
    return out


def family_fit_from_psych_affinity(programme_scores: dict[str, float]) -> dict[str, int]:
    """Reuse psych programme_affinity_tags → 3 KNUST families (0–100)."""
    from collections import defaultdict

    affinity_to_family = {
        "engineering": "Engineering",
        "medicine_health": "Health Sciences",
        "health": "Health Sciences",
        "natural_sciences": "Natural Sciences",
        "science": "Natural Sciences",
        "computing": "Engineering",
        "computing_it": "Engineering",
    }
    families: dict[str, float] = defaultdict(float)
    for key, score in (programme_scores or {}).items():
        family = affinity_to_family.get(str(key).lower().replace(" ", "_"))
        if family:
            families[family] += float(score)
    if not families:
        return {f: 50 for f in FAMILIES}
    return _max_normalize(dict(families))


def challenge_family_scores(
    subject_accuracies: dict[str, float],
) -> dict[str, int]:
    """Map rolling challenge accuracies onto families (neutral 50 if no data)."""
    buckets: dict[str, list[float]] = {f: [] for f in FAMILIES}
    for subject, acc in (subject_accuracies or {}).items():
        key = str(subject or "").strip().lower().replace(" ", "_")
        families = SUBJECT_TO_FAMILIES.get(key)
        if not families:
            continue
        value = max(0.0, min(1.0, float(acc))) * 100.0
        for f in families:
            buckets[f].append(value)
    raw = {
        f: (sum(vals) / len(vals) if vals else 50.0) for f, vals in buckets.items()
    }
    return {f: int(round(raw[f])) for f in FAMILIES}


def learning_family_scores(
    completed_lessons: list[Any] | None,
) -> dict[str, int]:
    """
    Soft signal from Learning Centre completions.
    Lesson ids/strings are weakly scanned for family keywords; default neutral.
    """
    raw = _neutral_families()
    if not completed_lessons:
        return {f: 50 for f in FAMILIES}
    text = " ".join(str(x).lower() for x in completed_lessons)
    if any(k in text for k in ("math", "engenharia", "engineer", "physics", "logic")):
        raw["Engineering"] += 20
    if any(k in text for k in ("bio", "health", "saúde", "saude", "medic", "enferm")):
        raw["Health Sciences"] += 20
    if any(k in text for k in ("science", "ciência", "ciencia", "quim", "chem", "comp")):
        raw["Natural Sciences"] += 20
    # Any lesson activity nudges all families slightly away from empty-profile look
    if completed_lessons:
        for f in FAMILIES:
            raw[f] += 5
    return _max_normalize(raw)


def trait_family_scores(
    behavioral_traits: dict[str, float],
    *,
    skill_estimates: dict[str, float] | None = None,
) -> dict[str, int]:
    """Soft trait / theta alignment without WASSCE grade boosts."""
    traits = {str(k): float(v) for k, v in (behavioral_traits or {}).items()}
    skills = skill_estimates or {}

    def trait(name: str, default: float = 0.5) -> float:
        for key, val in traits.items():
            if key.lower() == name.lower():
                # BehavioralProfile values may be 0–1 or 0–100
                return val / 100.0 if val > 1.5 else val
        return default

    math = float(skills.get("Math", 0)) + 3
    logic = float(skills.get("Logic", 0)) + 3
    science = float(skills.get("Science", 0)) + 3
    persistence = trait("Persistence", 0.5)
    carefulness = trait("Carefulness", 0.5)
    analytical = trait("analytical", trait("Analytical", 0.5))
    empathy = trait("empathy", trait("Empathy", 0.5))
    practical = trait("practical", trait("Practical", 0.5))

    raw = {
        "Engineering": math * 3 + science * 2 + persistence * 10 + analytical * 8 + practical * 6 + logic * 2,
        "Health Sciences": science * 3 + carefulness * 15 + empathy * 10,
        "Natural Sciences": science * 3 + math * 2 + persistence * 10 + analytical * 6,
    }
    return _max_normalize(raw)


def journey_confidence(*, phases_completed: int, session_count: int) -> float:
    """0–1: how much to trust / sharpen behavioural differences."""
    n_phases = max(0, int(phases_completed or 0))
    n_sessions = max(0, int(session_count or 0))
    return min(1.0, 0.35 + 0.25 * n_phases + 0.05 * min(20, n_sessions) / 20.0)


def combine_family_scores(
    *,
    psych: dict[str, int],
    challenge: dict[str, int],
    learning: dict[str, int],
    traits: dict[str, int],
    confidence: float,
) -> dict[str, int]:
    g = max(0.0, min(1.0, float(confidence)))
    combined: dict[str, float] = {}
    for f in FAMILIES:
        s = (
            W_PSYCH * float(psych.get(f, 50))
            + W_CHALLENGE * float(challenge.get(f, 50))
            + W_LEARNING * float(learning.get(f, 50))
            + W_TRAITS * float(traits.get(f, 50))
        )
        combined[f] = 50.0 + g * (s - 50.0)
    return _max_normalize(combined)


def _subject_overlap_bonus(
    programme_name: str,
    subject_accuracies: dict[str, float],
) -> float:
    name = str(programme_name or "").lower()
    strong = {
        str(s).lower().replace(" ", "_")
        for s, acc in (subject_accuracies or {}).items()
        if float(acc or 0) >= 0.6
    }
    if not strong:
        return 0.0
    bonus = 0.0
    for keywords, subjects in PROGRAMME_SUBJECT_HINTS:
        if any(k in name for k in keywords) and any(s in strong for s in subjects):
            bonus = max(bonus, 6.0)
    return bonus


def rank_programmes_behavioural(
    *,
    family_scores: dict[str, int],
    subject_accuracies: dict[str, float] | None = None,
    limit: int = 8,
) -> list[dict[str, Any]]:
    """
    Rank full KNUST catalogue by behavioural family fit (no cut-off gate).
    Returns enriched programme cards ready for UI / Recommendation rows.
    """
    cutoffs = load_knust_cutoffs()
    accuracies = subject_accuracies or {}
    scored: list[tuple[float, dict[str, Any]]] = []

    for row in cutoffs.get("programmes") or []:
        family = str(row.get("family") or "")
        atlas_family = FAMILY_ALIASES.get(family, family)
        if atlas_family not in FAMILIES:
            # Map Science → Natural Sciences already in FAMILY_ALIASES
            atlas_family = FAMILY_ALIASES.get(atlas_family, "Natural Sciences")
        base = float(family_scores.get(atlas_family, family_scores.get(family, 50)))
        programme = str(row.get("programme") or "")
        score = base + _subject_overlap_bonus(programme, accuracies)
        item = {
            "university": cutoffs.get("university", "KNUST"),
            "cycle": cutoffs.get("cycle"),
            "family": family,
            "programme": programme,
            "cutoff": row.get("cutoff"),
            "demand": row.get("demand"),
            "level": row.get("level", "Degree"),
            "eligibility_band": None,
            "aggregate": None,
            "family_fit_score": int(round(base)),
            "match_rank_score": score,
        }
        scored.append((score, item))

    scored.sort(key=lambda x: (-x[0], str(x[1].get("programme") or "")))
    cards: list[dict[str, Any]] = []
    for rank, (_, item) in enumerate(scored[:limit], start=1):
        why = (
            f"Ranked #{rank} from your psychometric profile and challenge activity "
            f"in Atlas so far (no WASSCE required)."
        )
        card = enrich_programme(item, why=why, method="behavioural_match")
        card["rank"] = rank
        cards.append(card)
    return cards


def build_behavioural_match(
    *,
    programme_affinity_scores: dict[str, float],
    subject_accuracies: dict[str, float],
    behavioral_traits: dict[str, float],
    skill_estimates: dict[str, float] | None = None,
    completed_lessons: list[Any] | None = None,
    phases_completed: int = 0,
    session_count: int = 0,
    limit: int = 8,
) -> dict[str, Any]:
    """Full BPM pipeline → family scores + ranked programme cards."""
    psych = family_fit_from_psych_affinity(programme_affinity_scores)
    challenge = challenge_family_scores(subject_accuracies)
    learning = learning_family_scores(completed_lessons)
    traits = trait_family_scores(behavioral_traits, skill_estimates=skill_estimates)
    confidence = journey_confidence(
        phases_completed=phases_completed,
        session_count=session_count,
    )
    family_scores = combine_family_scores(
        psych=psych,
        challenge=challenge,
        learning=learning,
        traits=traits,
        confidence=confidence,
    )
    programmes = rank_programmes_behavioural(
        family_scores=family_scores,
        subject_accuracies=subject_accuracies,
        limit=limit,
    )
    return {
        "family_fit_scores": family_scores,
        "confidence": confidence,
        "programmes": programmes,
        "signals": {
            "psych": psych,
            "challenge": challenge,
            "learning": learning,
            "traits": traits,
        },
    }
