"""
deepseek_service.py — DeepSeek AI integration for dynamic challenge generation

This module handles all DeepSeek API interactions for generating
SHS-standard challenge questions dynamically using the OpenAI-compatible API.
"""
import json
import logging
import re
from typing import Optional, Dict, Any

import httpx

from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# DeepSeek API configuration
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_CHAT_URL = f"{DEEPSEEK_BASE_URL}/v1/chat/completions"


class DeepSeekChallengeGenerator:
    """Service for generating SHS challenge questions using DeepSeek AI."""

    # Supported categories and programmes
    VALID_CATEGORIES = [
        "Logic",
        "Quantitative Thinking",
        "Scientific Thinking",
        "Verbal Reasoning",
        "Critical Thinking",
    ]

    VALID_PROGRAMMES = [
        "General Science",
        "General Arts",
    ]

    VALID_DIFFICULTY = [
        "Beginner",
        "Intermediate",
        "Advanced",
    ]

    # System prompt for consistent, high-quality question generation
    SYSTEM_PROMPT = """You are an expert SHS (Senior High School) educational assessment creator
specializing in Ghanaian curriculum standards.

Your task is to generate engaging, intellectually challenging questions that:
- Follow WAEC/SHS examination standards
- Are suitable for Ghanaian SHS students
- Focus on reasoning and deeper understanding, not memorization
- Are interactive and engaging
- Provide valuable learning through explanation

Important guidelines:
1. Create questions that develop critical thinking skills
2. Avoid simple factual recall questions — always test understanding, application, or analysis
3. Include distractors that reveal common misconceptions
4. Ensure explanations help students understand WHY the answer is correct
5. Make questions culturally relevant to Ghana context where appropriate
6. Use clear, unambiguous language
7. Keep explanations concise — maximum 3 short sentences

SCIENCE DOMAIN INSTRUCTIONS (when generating Scientific Thinking questions):
Rotate across ALL branches of science for diversity. Never repeat the same scientific concept twice in a row.
- Physics: mechanics, thermodynamics, optics, waves, electricity, magnetism, nuclear physics, quantum basics
- Chemistry: atomic structure, bonding, reactions, stoichiometry, organic chemistry, acids/bases, electrochemistry
- Biology: cell biology, genetics, evolution, ecology, human physiology, plant biology, microbiology
- Earth Science: geology, meteorology, oceanography, natural disasters, rock cycle, plate tectonics
- Astronomy: solar system, stellar evolution, cosmology basics, planetary science, space exploration
- Environmental Science: ecosystems, pollution, climate change, renewable energy, conservation
- Health Science: nutrition, disease, public health, pharmacology basics

Ensure each science question tests a real scientific principle with accurate data/facts. Include applied scenarios like experiments, observations, or real-world phenomena."""

    def __init__(self):
        """Initialize DeepSeek service."""
        if not settings.DEEPSEEK_API_KEY:
            logger.warning("DEEPSEEK_API_KEY not configured. DeepSeek integration will not work.")

    def validate_parameters(
        self,
        category: str,
        difficulty: str,
        programme: str,
    ) -> tuple[bool, Optional[str]]:
        """
        Validate request parameters.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if category not in self.VALID_CATEGORIES:
            return False, f"Invalid category. Valid options: {', '.join(self.VALID_CATEGORIES)}"

        if difficulty not in self.VALID_DIFFICULTY:
            return False, f"Invalid difficulty. Valid options: {', '.join(self.VALID_DIFFICULTY)}"

        if programme not in self.VALID_PROGRAMMES:
            return False, f"Invalid programme. Valid options: {', '.join(self.VALID_PROGRAMMES)}"

        return True, None

    def _create_prompt(
        self,
        category: str,
        difficulty: str,
        programme: str,
        concept: Optional[str] = None,
    ) -> str:
        """
        Create the prompt for DeepSeek to generate a question.

        Args:
            category: Question category
            difficulty: Difficulty level
            programme: SHS programme (General Science or General Arts)
            concept: Optional specific concept to focus on

        Returns:
            Formatted prompt for DeepSeek
        """
        concept_text = f"\nFocus on this concept: {concept}" if concept else ""

        prompt = f"""Generate ONE SHS-level challenge question in JSON format with the following specifications:

Category: {category}
Difficulty: {difficulty}
Programme: {programme}
{concept_text}

For SCIENTIFIC THINKING category questions specifically:
- Include real scientific data, phenomena, or principles
- Use applied scenarios: experiments, observations, calculations, case studies
- Cover diverse branches of science: physics, chemistry, biology, earth science, astronomy, environmental science, health science
- Feature a specific real scientific concept as the `concept` field

Return ONLY valid JSON (no markdown, no code blocks) matching this structure:
{{
    "category": "{category}",
    "difficulty": "{difficulty}",
    "concept": "specific scientific concept being tested (e.g., 'Newton's Second Law' or 'Photosynthesis')",
    "question": "The actual question text",
    "options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
    ],
    "correct_answer": "Option A",
    "explanation": "Detailed explanation of why this answer is correct and what students should understand"
}}

Important:
- Ensure the question tests reasoning, not just memorization
- Make options realistic but distinguishable by understanding, not guessing
- The explanation should be educational and help students learn
- Correct answer must be one of the four options
- All text should be clear and appropriate for SHS students"""

        return prompt

    async def generate_challenge(
        self,
        category: str,
        difficulty: str,
        programme: str,
        concept: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a single SHS challenge question using DeepSeek AI.

        Args:
            category: Question category (Logic, Quantitative Thinking, etc.)
            difficulty: Difficulty level (Beginner, Intermediate, Advanced)
            programme: SHS programme (General Science, General Arts)
            concept: Optional specific concept to focus on

        Returns:
            Dictionary with generated question data or error information
        """
        # Validate parameters
        is_valid, error_msg = self.validate_parameters(category, difficulty, programme)
        if not is_valid:
            return {
                "success": False,
                "error": error_msg,
            }

        # Check API key configuration
        if not settings.NVIDIA_API_KEY and not settings.DEEPSEEK_API_KEY:
            return {
                "success": False,
                "error": "Neither NVIDIA_API_KEY nor DEEPSEEK_API_KEY is configured. Please set them in your .env file.",
            }

        prompt = self._create_prompt(category, difficulty, programme, concept)
        response_text = ""

        # 1. Try NVIDIA if API key is provided
        if settings.NVIDIA_API_KEY:
            try:
                logger.info(f"Generating challenge via NVIDIA API using model: {settings.NVIDIA_MODEL}")
                headers = {
                    "Authorization": f"Bearer {settings.NVIDIA_API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": settings.NVIDIA_MODEL,
                    "messages": [
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.5,
                    "top_p": 1.0,
                    "max_tokens": 2048
                }
                async with httpx.AsyncClient(timeout=120.0) as client:
                    response = await client.post(
                        "https://integrate.api.nvidia.com/v1/chat/completions",
                        headers=headers,
                        json=payload
                    )
                    response.raise_for_status()
                    result_data = response.json()
                    response_text = result_data["choices"][0]["message"]["content"]
                    logger.info("Successfully received response from NVIDIA API.")
            except httpx.ReadTimeout:
                err_msg = "NVIDIA API request timed out after 120s. The model may be overloaded — please retry."
                logger.error(err_msg)
                if not settings.DEEPSEEK_API_KEY:
                    return {"success": False, "error": err_msg}
                logger.info("Falling back to DeepSeek after timeout...")
            except httpx.HTTPStatusError as e:
                err_msg = f"NVIDIA API HTTP error {e.response.status_code}: {e.response.text}"
                logger.error(err_msg)
                if not settings.DEEPSEEK_API_KEY:
                    return {"success": False, "error": err_msg}
                logger.info("Falling back to DeepSeek after HTTP error...")
            except Exception as e:
                err_msg = f"NVIDIA API error ({type(e).__name__}): {e!r}"
                logger.error(err_msg)
                # If NVIDIA fails, fall back to DeepSeek if possible
                if not settings.DEEPSEEK_API_KEY:
                    return {"success": False, "error": err_msg}
                logger.info("Falling back to DeepSeek...")

        # 2. Fall back or use DeepSeek
        if not response_text and settings.DEEPSEEK_API_KEY:
            try:
                logger.info(f"Generating challenge via DeepSeek API using model: {settings.DEEPSEEK_MODEL}")
                headers = {
                    "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": settings.DEEPSEEK_MODEL,
                    "messages": [
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.5,
                    "top_p": 1.0,
                    "max_tokens": 2048,
                    "stream": False,
                }
                async with httpx.AsyncClient(timeout=120.0) as client:
                    response = await client.post(
                        DEEPSEEK_CHAT_URL,
                        headers=headers,
                        json=payload
                    )
                    response.raise_for_status()
                    result_data = response.json()
                    response_text = result_data["choices"][0]["message"]["content"]
                    logger.info("Successfully received response from DeepSeek API.")

            except httpx.HTTPStatusError as e:
                err_msg = f"DeepSeek API HTTP error {e.response.status_code}: {e.response.text}"
                logger.error(err_msg)
                return {"success": False, "error": err_msg}
            except httpx.TimeoutException:
                err_msg = "DeepSeek API request timed out after 120s."
                logger.error(err_msg)
                return {"success": False, "error": err_msg}
            except Exception as e:
                logger.error(f"DeepSeek API error: {e}")
                return {
                    "success": False,
                    "error": f"DeepSeek API error: {str(e)}",
                }

        if not response_text:
            return {
                "success": False,
                "error": "Failed to get response from AI engines.",
            }

        try:
            # Parse the response
            response_text = response_text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]  # Remove ```json
            if response_text.startswith("```"):
                response_text = response_text[3:]  # Remove ```
            if response_text.endswith("```"):
                response_text = response_text[:-3]  # Remove trailing ```

            response_text = response_text.strip()

            # Parse JSON
            question_data = json.loads(response_text)

            # Validate the structure
            required_fields = [
                "category",
                "difficulty",
                "concept",
                "question",
                "options",
                "correct_answer",
                "explanation",
            ]

            missing_fields = [f for f in required_fields if f not in question_data]
            if missing_fields:
                return {
                    "success": False,
                    "error": f"AI response missing required fields: {', '.join(missing_fields)}",
                }

            # Validate options
            if not isinstance(question_data["options"], list) or len(question_data["options"]) != 4:
                return {
                    "success": False,
                    "error": f"Question must have exactly 4 options. Got: {question_data.get('options')}",
                }

            # Normalize correct_answer: models may return:
            #   - A letter index ("A", "B", "C", "D")
            #   - "Option X" format ("Option B")
            #   - The full option text
            #   - A numeric index (0-3)
            # Resolve to the matching option text.
            answer = question_data["correct_answer"]
            options = question_data["options"]

            # Helper: find option by exact match, prefix match, or fuzzy match
            def _resolve_answer(ans: str, opts: list) -> str | None:
                # 1. Exact match
                if ans in opts:
                    return ans
                # 2. Single uppercase letter → index
                LETTER_MAP = {"A": 0, "B": 1, "C": 2, "D": 3}
                if ans in LETTER_MAP:
                    idx = LETTER_MAP[ans]
                    if idx < len(opts):
                        return opts[idx]
                # 3. "Option X" format → extract letter
                m = re.match(r"^[Oo]ption\s*([A-Da-d])\s*$", ans.strip())
                if m:
                    idx = LETTER_MAP[m.group(1).upper()]
                    if idx < len(opts):
                        return opts[idx]
                # 4. Numeric string → index
                if ans.isdigit():
                    idx = int(ans)
                    if 0 <= idx < len(opts):
                        return opts[idx]
                return None

            resolved = _resolve_answer(answer, options)
            if resolved:
                question_data["correct_answer"] = resolved
            else:
                return {
                    "success": False,
                    "error": f"Correct answer '{answer}' does not match any option in {options}.",
                }

            # Return success response
            return {
                "success": True,
                "data": question_data,
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI JSON response: {e}. Raw response: {response_text}")
            return {
                "success": False,
                "error": f"Failed to parse AI response as JSON: {str(e)}",
            }

        except Exception as e:
            logger.error(f"AI Generation post-processing error: {e}")
            return {
                "success": False,
                "error": f"AI Generation post-processing error: {str(e)}",
            }


# Create a singleton instance
deepseek_generator = DeepSeekChallengeGenerator()


async def generate_challenge_question(
    category: str,
    difficulty: str,
    programme: str,
    concept: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Async wrapper for challenge generation.

    This function can be called from FastAPI routes.
    """
    return await deepseek_generator.generate_challenge(
        category=category,
        difficulty=difficulty,
        programme=programme,
        concept=concept,
    )
