"""
assessment/recommendation_engine.py
───────────────────────────────────
Programme recommendations are strictly from the KNUST Science / Engineering /
Health cut-off catalogue, gated by the student's uploaded WASSCE grades.

Soft signals (challenge thetas, behaviour, pathway) only rank programmes
*inside* eligibility bands. They never invent programmes outside the catalogue.
"""
from typing import Any, Dict, List, Optional


GRADE_SCORE = {
    "A1": 100,
    "A": 95,
    "B2": 90,
    "B3": 82,
    "B": 85,
    "C4": 74,
    "C5": 68,
    "C6": 62,
    "C": 68,
    "D7": 48,
    "D": 48,
    "E8": 36,
    "E": 36,
    "F9": 18,
    "F": 18,
}

# Soft ranking keys map onto KNUST families in the cut-off document only.
KNUST_FAMILY_KEYS = (
    "Health Sciences",
    "Engineering",
    "Natural Sciences",  # maps from document family "Science"
)


class RecommendationEngine:
    """Generate KNUST programme recommendations from uploaded grades + cut-offs."""

    def __init__(
        self,
        skill_estimates: Dict[str, float],
        behavioral_traits: Dict[str, float],
        academic_grades: Optional[List[Dict[str, str]]] = None,
        programme: Optional[str] = None,
        learner_profile: Optional[Dict[str, Any]] = None,
    ):
        self.skill_estimates = skill_estimates or {}
        self.behavioral_traits = behavioral_traits or {}
        self.academic_grades = academic_grades or []
        self.programme = programme or ""
        self.learner_profile = learner_profile or {}

        if self.skill_estimates:
            overall_theta = sum(self.skill_estimates.values()) / max(1, len(self.skill_estimates))
            self.academic_score = min(100, max(0, int((overall_theta + 3) / 6 * 100)))
        elif self.academic_grades:
            scores = [
                GRADE_SCORE.get(str(g.get("grade", "")).upper(), 55)
                for g in self.academic_grades
            ]
            self.academic_score = int(sum(scores) / max(1, len(scores)))
        else:
            self.academic_score = 60

        self.performance_level = self._get_performance_level()

    def _get_performance_level(self) -> str:
        if self.academic_score >= 80:
            return "Excellent"
        if self.academic_score >= 65:
            return "Good"
        if self.academic_score >= 50:
            return "Average"
        return "Needs Improvement"

    def _knust_family_fit_scores(self) -> Dict[str, int]:
        """Soft 0–100 scores for the three KNUST families only (for in-band ranking)."""
        math_theta = self.skill_estimates.get("Math", 0)
        logic_theta = self.skill_estimates.get("Logic", 0)
        science_theta = self.skill_estimates.get("Science", 0)
        persistence = self.behavioral_traits.get("Persistence", 0.5)
        carefulness = self.behavioral_traits.get("Carefulness", 0.5)

        math = math_theta + 3
        logic = logic_theta + 3
        science = science_theta + 3

        raw = {
            "Engineering": math * 3 + science * 2 + persistence * 10,
            "Health Sciences": science * 3 + carefulness * 15,
            "Natural Sciences": science * 3 + math * 2 + persistence * 10,
        }

        # Grade subject boosts (still soft ranking only)
        for row in self.academic_grades:
            subject = str(row.get("subject", "")).lower()
            grade = str(row.get("grade", "")).upper()
            points = GRADE_SCORE.get(grade, 55) / 10.0
            if any(k in subject for k in ("math", "add math", "elective math")):
                raw["Engineering"] += points * 1.4
                raw["Natural Sciences"] += points
            if any(k in subject for k in ("physics", "chemistry", "biology", "science")):
                raw["Natural Sciences"] += points * 1.4
                raw["Health Sciences"] += points * 1.2
                raw["Engineering"] += points
            if any(k in subject for k in ("ict", "computing", "computer")):
                raw["Natural Sciences"] += points * 1.2  # CS sits under Science cut-offs
                raw["Engineering"] += points

        prog = self.programme.lower()
        if "science" in prog:
            raw["Natural Sciences"] += 8
            raw["Engineering"] += 6
            raw["Health Sciences"] += 5

        focus = str(self.learner_profile.get("recommended_focus") or "").lower()
        if "logic" in focus or "problem" in focus:
            raw["Engineering"] += 3
            raw["Natural Sciences"] += 2
        if "science" in focus:
            raw["Natural Sciences"] += 4
            raw["Health Sciences"] += 3

        max_score = max(raw.values()) if raw.values() else 1
        if max_score <= 0:
            max_score = 1
        return {k: int((v / max_score) * 100) for k, v in raw.items()}

    @staticmethod
    def _programme_cards_from_bands(knust: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Flatten eligible + stretch into the primary recommendation list (document only)."""
        bands = knust.get("bands") or {}
        cards: List[Dict[str, Any]] = []
        for band_key, label in (("eligible", "Eligible"), ("stretch", "Stretch")):
            for item in bands.get(band_key) or []:
                cards.append(
                    {
                        "programme": item["programme"],
                        "programme_family": item.get("family"),
                        "family": item.get("family"),
                        "university": item.get("university", "KNUST"),
                        "cycle": item.get("cycle"),
                        "cutoff": item.get("cutoff"),
                        "demand": item.get("demand"),
                        "eligibility_band": band_key,
                        "fit_score": int(item.get("family_fit_score") or 0),
                        "fit_level": label,
                        "headroom": item.get("headroom"),
                        "aggregate": item.get("aggregate"),
                        "description": (
                            f"KNUST {item.get('family')} programme from the "
                            f"{item.get('cycle') or '2025/2026'} cut-off list."
                        ),
                        "why_good_fit": (
                            f"Your estimated aggregate "
                            f"{item.get('aggregate')} vs cut-off ≤ {item.get('cutoff')} "
                            f"({label.lower()} band)."
                        ),
                        "source": "knust_cutoffs",
                    }
                )
        return cards

    def generate_recommendations(self) -> Dict[str, Any]:
        from app.recommendations.cutoffs import apply_cutoff_boundaries
        from app.recommendations.presentation import select_suitable_and_competitive

        if not self.academic_grades:
            return {
                "recommendations": [],
                "suitable_programmes": [],
                "competitive_programmes": [],
                "performance_level": self.performance_level,
                "academic_score": self.academic_score,
                "summary_message": (
                    "Upload readable WASSCE / academic results first. "
                    "Atlas combines your results, aggregate, learning profile, "
                    "and challenge performance to recommend suitable programmes."
                ),
                "detailed_message": (
                    "Grades are required so Atlas can calculate your aggregate "
                    "and keep recommendations close to your results."
                ),
                "grades_used": 0,
                "knust": None,
                "admission_insights": None,
                "error": "grades_required",
            }

        family_fit = self._knust_family_fit_scores()
        knust = apply_cutoff_boundaries(
            grades=self.academic_grades,
            family_fit_scores=family_fit,
            limit_per_band=50,
        )
        selected = select_suitable_and_competitive(
            grades=self.academic_grades,
            family_fit_scores=family_fit,
            limit=8,
        )
        agg = knust.get("aggregate") or {}
        suitable = selected.get("suitable") or []
        competitive = selected.get("competitive") or []

        if agg.get("aggregate") is None:
            summary = (
                "Could not compute a WASSCE aggregate from the uploaded grades "
                "(need Core English, Core Mathematics, and enough other subjects). "
                "Re-upload a clearer results slip to unlock programme recommendations."
            )
            suitable = []
            competitive = []
        else:
            complete = "complete" if agg.get("complete") else "provisional"
            summary = (
                f"Your estimated WASSCE aggregate is {agg['aggregate']} ({complete}). "
                f"Atlas ranked programmes that fit your psychometric profile and challenge "
                f"performance, then kept those whose admission points sit near your aggregate."
            )
            if not suitable and not competitive:
                summary += (
                    " No close matches were found for this aggregate yet — "
                    "try confirming your grades or strengthening weaker subjects."
                )

        return {
            "recommendations": suitable,
            "suitable_programmes": suitable,
            "competitive_programmes": competitive,
            "performance_level": self.performance_level,
            "academic_score": self.academic_score,
            "summary_message": summary,
            "detailed_message": (
                "Recommendations combine academic results, aggregate, psychometric profile, "
                "and challenge performance. Competitive programmes match your strengths but "
                "are typically more selective than your current aggregate."
            ),
            "grades_used": len(self.academic_grades),
            "knust": knust,
            "admission_insights": {
                "aggregate": agg.get("aggregate"),
                "complete": agg.get("complete"),
                "nearby_range": 2,
            },
            "error": None if suitable or competitive or agg.get("aggregate") is not None else "aggregate_unavailable",
        }
