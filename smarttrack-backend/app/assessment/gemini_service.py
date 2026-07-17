"""
gemini_service.py — DEPRECATED

This module has been replaced by deepseek_service.py.
It remains here as a backward-compatibility shim so that
any existing imports still resolve.

Please update your imports to use `deepseek_service` instead.
"""
import warnings
from typing import Optional, Dict, Any

from app.assessment.deepseek_service import (
    DeepSeekChallengeGenerator as GeminiChallengeGenerator,
    generate_challenge_question,
    deepseek_generator as gemini_generator,
)

warnings.warn(
    "gemini_service is deprecated. Use deepseek_service instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["GeminiChallengeGenerator", "generate_challenge_question", "gemini_generator"]
