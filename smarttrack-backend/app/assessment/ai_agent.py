import json
from typing import Dict, Optional, List

from app.assessment.gemini_service import generate_challenge_question


async def generate_adaptive_questions(domain: str, target_difficulty: float, count: int = 3) -> List[Dict]:
    """
    Generate real questions via NVIDIA API on the fly.

    Returns a list of question dicts with keys:
      domain, question, options, correct_answer, difficulty_b, explanation

    Falls back to an empty list if generation fails (prefetch_manager
    handles the background pipeline instead).
    """
    # Map our domain names to the categories Gemini/NVIDIA understand
    DOMAIN_TO_CATEGORY = {
        "Math": "Quantitative Thinking",
        "Verbal": "Verbal Reasoning",
        "Science": "Scientific Thinking",
        "Logic": "Logic",
        "General": "Critical Thinking",
    }
    category = DOMAIN_TO_CATEGORY.get(domain, "Critical Thinking")

    # Map theta to a difficulty label
    if target_difficulty < -1.0:
        diff_label = "Beginner"
    elif target_difficulty > 1.0:
        diff_label = "Advanced"
    else:
        diff_label = "Intermediate"

    generated = []
    for i in range(count):
        try:
            result = await generate_challenge_question(
                category=category,
                difficulty=diff_label,
                programme="General Science",  # fallback if user category unknown
            )
        except Exception:
            continue

        if not result.get("success"):
            continue

        ai_q = result["data"]
        letters = ["A", "B", "C", "D"]
        options_dict: Dict[str, str] = {}
        for idx, opt in enumerate(ai_q.get("options", [])):
            if idx < len(letters):
                options_dict[letters[idx]] = str(opt)

        # Resolve correct_answer to a letter
        answer = ai_q.get("correct_answer", "")
        if answer in letters:
            correct_letter = answer
        elif answer in ai_q.get("options", []):
            correct_letter = letters[ai_q["options"].index(answer)]
        else:
            correct_letter = "A"

        generated.append({
            "domain": domain,
            "question": ai_q["question"],
            "options": options_dict,
            "correct_answer": correct_letter,
            "difficulty_b": target_difficulty,
            "explanation": ai_q.get("explanation", ""),
        })

    return generated


async def get_ai_explanation(
    question_text: str,
    selected_option: str,
    correct_option: str,
    options: Dict[str, str],
) -> str:
    """Provide a concise explanation without an extra API call."""
    # No separate API call — explanations were already generated/returned
    # alongside the question data. This function returns a simple fallback.
    return f"The correct answer is {correct_option}. Review the related concepts to strengthen your understanding."
