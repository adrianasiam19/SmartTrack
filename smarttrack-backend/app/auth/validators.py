"""
auth/validators.py
──────────────────
Password validation utilities for secure registration.
"""
import re


class PasswordValidationError(ValueError):
    """Custom exception for password validation errors."""
    pass


def validate_password_strength(password: str) -> None:
    """
    Validate password strength according to security requirements.
    
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character (@, #, _, !, etc.)
    
    Raises:
        PasswordValidationError: If password doesn't meet requirements
    """
    if len(password) < 8:
        raise PasswordValidationError(
            "Password must be at least 8 characters long."
        )
    
    if not re.search(r'[A-Z]', password):
        raise PasswordValidationError(
            "Password must include at least one uppercase letter."
        )
    
    if not re.search(r'[a-z]', password):
        raise PasswordValidationError(
            "Password must include at least one lowercase letter."
        )
    
    if not re.search(r'[0-9]', password):
        raise PasswordValidationError(
            "Password must include at least one number."
        )
    
    # Check for special characters: @, #, _, !, $, %, ^, &, *, etc.
    if not re.search(r'[@#_!$%^&*\-+=\[\]{};:\'",.<>?/\\|`~()]', password):
        raise PasswordValidationError(
            "Password must include at least one special character (@, #, _, !, etc.)."
        )


def get_password_strength_message() -> str:
    """
    Return user-friendly password requirements message.
    """
    return (
        "Password must be at least 8 characters and include uppercase, "
        "lowercase, number, and special character (@, #, _, !, etc.)."
    )
