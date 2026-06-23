"""
assessment/recommendation_engine.py
───────────────────────────────────
Intelligent recommendation engine that generates programme recommendations
based on Item Response Theory (IRT) thetas and behavioral traits.
"""
from typing import Dict, Any, List


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
            "keywords": ["health", "medicine", "nursing", "nursing", "dentistry"],
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
    ):
        """
        Initialize recommendation engine with Stealth Assessment inputs.
        
        Args:
            skill_estimates: Dictionary mapping domains to IRT theta scores (e.g., Math: 1.5)
            behavioral_traits: Dictionary mapping traits to values (0.0 to 1.0)
        """
        self.skill_estimates = skill_estimates or {}
        self.behavioral_traits = behavioral_traits or {}
        
        # Calculate a pseudo academic score out of 100 based on thetas
        # Assuming theta ranges mostly from -3 to 3. Map -2 to 30%, 0 to 65%, 2 to 95%
        overall_theta = sum(self.skill_estimates.values()) / max(1, len(self.skill_estimates))
        self.academic_score = min(100, max(0, int((overall_theta + 3) / 6 * 100)))
        
        self.performance_level = self._get_performance_level()
        
    def _get_performance_level(self) -> str:
        if self.academic_score >= 80:
            return "Excellent"
        elif self.academic_score >= 65:
            return "Good"
        elif self.academic_score >= 50:
            return "Average"
        else:
            return "Needs Improvement"
    
    def _calculate_programme_fit(self) -> Dict[str, int]:
        """Calculate fit scores for each programme category based on domains and behaviors."""
        fit_scores = {programme: 0 for programme in self.PROGRAMMES.keys()}
        
        math_theta = self.skill_estimates.get("Math", 0)
        logic_theta = self.skill_estimates.get("Logic", 0)
        verbal_theta = self.skill_estimates.get("Verbal", 0)
        science_theta = self.skill_estimates.get("Science", 0)
        
        persistence = self.behavioral_traits.get("Persistence", 0.5)
        speed = self.behavioral_traits.get("Processing Speed", 0.5)
        carefulness = self.behavioral_traits.get("Carefulness", 0.5)

        # Baseline offset for thetas to make them positive for weighting (assume min is -3)
        math = math_theta + 3
        logic = logic_theta + 3
        verbal = verbal_theta + 3
        science = science_theta + 3

        # Computing & IT: Logic, Math, Persistence
        fit_scores["Computing & IT"] = logic * 3 + math * 2 + persistence * 10
        
        # Engineering: Math, Science, Persistence
        fit_scores["Engineering"] = math * 3 + science * 2 + persistence * 10
        
        # Health Sciences: Science, Carefulness
        fit_scores["Health Sciences"] = science * 3 + carefulness * 15
        
        # Business & Economics: Math, Verbal, Speed
        fit_scores["Business & Economics"] = math * 2 + verbal * 2 + logic * 1 + speed * 10
        
        # Natural Sciences: Science, Math, Persistence
        fit_scores["Natural Sciences"] = science * 3 + math * 2 + persistence * 10
        
        # Law & Humanities: Verbal, Logic, Carefulness
        fit_scores["Law & Humanities"] = verbal * 3 + logic * 2 + carefulness * 10
        
        # Education & Social Sciences: Verbal, General
        fit_scores["Education & Social Sciences"] = verbal * 3 + carefulness * 10
        
        return fit_scores
    
    def _normalize_scores(self, fit_scores: Dict[str, float]) -> Dict[str, int]:
        """Normalize fit scores to 0-100 range."""
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
        
        recommendations = [
            {
                "programme_family": programme,
                "fit_score": score,
                "fit_level": "Strong Match" if score >= 80 else "Good Match" if score >= 60 else "Moderate Match",
                "description": f"Focuses on {self.PROGRAMMES[programme]['keywords'][0]} and related fields.",
                "why_good_fit": "This programme aligns well with your demonstrated cognitive strengths and behavioral profile.",
            }
            for programme, score in sorted_programmes
        ]
        
        return {
            "recommendations": recommendations,
            "performance_level": self.performance_level,
            "academic_score": self.academic_score,
            "summary_message": f"Based on your stealth assessment, your overall estimated performance is {self.academic_score}%.",
            "detailed_message": "These recommendations consider your fluid intelligence, logical problem solving, and behavioral patterns.",
        }
