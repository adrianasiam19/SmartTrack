"""
assessment/recommendation_engine.py
───────────────────────────────────
Intelligent recommendation engine that generates programme recommendations
based on Item Response Theory (IRT) thetas, behavioral traits, and academic grades.
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


class RecommendationEngine:
    """Generate dynamic programme recommendations based on stealth assessment."""

    PROGRAMMES = {
        "Computing & IT": {
            "short_name": "Computing / IT",
            "foundation": "Programming fundamentals, algorithms, data structures",
            "keywords": ["computing", "programming", "software", "technology"],
        },
        "Engineering": {
            "short_name": "Engineering",
            "foundation": "Mathematics, physics, technical drawing",
            "keywords": ["engineering", "mechanical", "electrical", "civil"],
        },
        "Health Sciences": {
            "short_name": "Health Sciences",
            "foundation": "Biology, chemistry, human sciences",
            "keywords": ["health", "medicine", "nursing", "dentistry"],
        },
        "Business & Economics": {
            "short_name": "Business & Economics",
            "foundation": "Mathematical reasoning, business fundamentals",
            "keywords": ["business", "economics", "finance", "management"],
        },
        "Natural Sciences": {
            "short_name": "Natural Sciences",
            "foundation": "Physics, chemistry, biology, mathematics",
            "keywords": ["science", "physics", "chemistry", "biology"],
        },
        "Law & Humanities": {
            "short_name": "Law & Humanities",
            "foundation": "Analytical thinking, reasoning, communication",
            "keywords": ["law", "humanities", "english", "social"],
        },
        "Education & Social Sciences": {
            "short_name": "Education & Social Sciences",
            "foundation": "Communication, interpersonal skills, analytical reasoning",
            "keywords": ["education", "social", "psychology", "sociology"],
        },
    }

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

    def _grade_boosts(self) -> Dict[str, float]:
        """Map subject grades into soft programme boosts."""
        boosts = {programme: 0.0 for programme in self.PROGRAMMES}
        for row in self.academic_grades:
            subject = str(row.get("subject", "")).lower()
            grade = str(row.get("grade", "")).upper()
            points = GRADE_SCORE.get(grade, 55) / 10.0

            if any(k in subject for k in ("math", "add math", "elective math")):
                boosts["Engineering"] += points * 1.4
                boosts["Computing & IT"] += points * 1.2
                boosts["Natural Sciences"] += points
                boosts["Business & Economics"] += points * 0.8
            if any(k in subject for k in ("physics", "chemistry", "biology", "science")):
                boosts["Natural Sciences"] += points * 1.4
                boosts["Health Sciences"] += points * 1.2
                boosts["Engineering"] += points
            if any(k in subject for k in ("english", "literature", "government", "history")):
                boosts["Law & Humanities"] += points * 1.4
                boosts["Education & Social Sciences"] += points
            if any(k in subject for k in ("accounting", "business", "economics", "commerce")):
                boosts["Business & Economics"] += points * 1.5
            if any(k in subject for k in ("ict", "computing", "computer")):
                boosts["Computing & IT"] += points * 1.6

        prog = self.programme.lower()
        if "science" in prog:
            boosts["Natural Sciences"] += 8
            boosts["Engineering"] += 6
            boosts["Health Sciences"] += 5
            boosts["Computing & IT"] += 4
        elif "art" in prog:
            boosts["Law & Humanities"] += 8
            boosts["Education & Social Sciences"] += 6
            boosts["Business & Economics"] += 4
        elif "business" in prog:
            boosts["Business & Economics"] += 10
            boosts["Computing & IT"] += 3

        focus = str(self.learner_profile.get("recommended_focus") or "").lower()
        challenges = " ".join(
            str(c) for c in (self.learner_profile.get("recommended_challenges") or [])
        ).lower()
        blob = f"{focus} {challenges}"
        if "logic" in blob or "problem" in blob:
            boosts["Computing & IT"] += 4
            boosts["Engineering"] += 3
        if "science" in blob:
            boosts["Natural Sciences"] += 4
            boosts["Health Sciences"] += 3
        if "english" in blob or "verbal" in blob or "communication" in blob:
            boosts["Law & Humanities"] += 4
            boosts["Education & Social Sciences"] += 3

        return boosts

    def _calculate_programme_fit(self) -> Dict[str, float]:
        fit_scores = {programme: 0.0 for programme in self.PROGRAMMES.keys()}

        math_theta = self.skill_estimates.get("Math", 0)
        logic_theta = self.skill_estimates.get("Logic", 0)
        verbal_theta = self.skill_estimates.get("Verbal", 0)
        science_theta = self.skill_estimates.get("Science", 0)

        persistence = self.behavioral_traits.get("Persistence", 0.5)
        speed = self.behavioral_traits.get("Processing Speed", 0.5)
        carefulness = self.behavioral_traits.get("Carefulness", 0.5)

        math = math_theta + 3
        logic = logic_theta + 3
        verbal = verbal_theta + 3
        science = science_theta + 3

        fit_scores["Computing & IT"] = logic * 3 + math * 2 + persistence * 10
        fit_scores["Engineering"] = math * 3 + science * 2 + persistence * 10
        fit_scores["Health Sciences"] = science * 3 + carefulness * 15
        fit_scores["Business & Economics"] = math * 2 + verbal * 2 + logic * 1 + speed * 10
        fit_scores["Natural Sciences"] = science * 3 + math * 2 + persistence * 10
        fit_scores["Law & Humanities"] = verbal * 3 + logic * 2 + carefulness * 10
        fit_scores["Education & Social Sciences"] = verbal * 3 + carefulness * 10

        for programme, boost in self._grade_boosts().items():
            fit_scores[programme] = fit_scores.get(programme, 0) + boost

        return fit_scores

    def _normalize_scores(self, fit_scores: Dict[str, float]) -> Dict[str, int]:
        max_score = max(fit_scores.values()) if fit_scores.values() else 1
        if max_score <= 0:
            max_score = 1

        return {
            programme: int((score / max_score) * 100)
            for programme, score in fit_scores.items()
        }

    def generate_recommendations(self) -> Dict[str, Any]:
        fit_scores = self._calculate_programme_fit()
        normalized = self._normalize_scores(fit_scores)
        sorted_programmes = sorted(normalized.items(), key=lambda x: x[1], reverse=True)

        sources = []
        if self.skill_estimates:
            sources.append("challenge performance")
        if self.academic_grades:
            sources.append("uploaded academic results")
        if self.learner_profile:
            sources.append("Starter Arena profile")
        if self.programme:
            sources.append(f"your {self.programme} pathway")
        source_text = ", ".join(sources) if sources else "your Atlas profile"

        recommendations = [
            {
                "programme_family": programme,
                "fit_score": score,
                "fit_level": (
                    "Strong Match"
                    if score >= 80
                    else "Good Match"
                    if score >= 60
                    else "Moderate Match"
                ),
                "description": (
                    f"Focuses on {self.PROGRAMMES[programme]['keywords'][0]} and related fields."
                ),
                "why_good_fit": (
                    "This programme aligns well with your demonstrated strengths "
                    f"and {source_text}."
                ),
                "foundation": self.PROGRAMMES[programme]["foundation"],
            }
            for programme, score in sorted_programmes
        ]

        return {
            "recommendations": recommendations,
            "performance_level": self.performance_level,
            "academic_score": self.academic_score,
            "summary_message": (
                f"Based on {source_text}, your overall estimated performance is "
                f"{self.academic_score}%."
            ),
            "detailed_message": (
                "These recommendations combine cognitive signals, behavioural patterns, "
                "and any academic results you uploaded."
            ),
            "grades_used": len(self.academic_grades),
        }
