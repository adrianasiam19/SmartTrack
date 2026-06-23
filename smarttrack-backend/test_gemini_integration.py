"""
test_gemini_integration.py — Test script for Gemini AI integration

This script tests the Gemini integration without running the full FastAPI server.
Run it with: python test_gemini_integration.py
"""
import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.assessment.gemini_service import gemini_generator


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_result(result: dict):
    """Pretty print the result."""
    if result["success"]:
        challenge = result["data"]
        print("[PASS] CHALLENGE GENERATED SUCCESSFULLY!\n")
        print(f"Category:    {challenge['category']}")
        print(f"Difficulty:  {challenge['difficulty']}")
        print(f"Concept:     {challenge['concept']}\n")
        print(f"Question:\n{challenge['question']}\n")
        print("Options:")
        for i, option in enumerate(challenge['options'], 1):
            print(f"  {i}. {option}")
        print(f"\nCorrect Answer: {challenge['correct_answer']}\n")
        print(f"Explanation:\n{challenge['explanation']}")
    else:
        print(f"[FAIL] ERROR: {result['error']}")


async def test_gemini_integration():
    """Test the Gemini integration."""
    print_section("GEMINI AI INTEGRATION TEST")
    
    # Check API key configuration
    print("1. Checking Configuration...")
    if not settings.NVIDIA_API_KEY and not settings.GEMINI_API_KEY:
        print("[WARN] Neither NVIDIA_API_KEY nor GEMINI_API_KEY is set in .env file")
        print("       Please add at least one API key to .env and try again\n")
        return False
    else:
        if settings.NVIDIA_API_KEY:
            print("[PASS] NVIDIA_API_KEY is configured")
        if settings.GEMINI_API_KEY:
            print("[PASS] GEMINI_API_KEY is configured")
        print()
    
    # Test parameters validation
    print("2. Testing Parameter Validation...")
    
    # Valid parameters
    valid_result = gemini_generator.validate_parameters(
        category="Logic",
        difficulty="Intermediate",
        programme="General Science"
    )
    if valid_result[0]:
        print("[PASS] Valid parameters accepted\n")
    else:
        print(f"[FAIL] Valid parameters rejected: {valid_result[1]}\n")
        return False
    
    # Invalid category
    invalid_result = gemini_generator.validate_parameters(
        category="InvalidCategory",
        difficulty="Intermediate",
        programme="General Science"
    )
    if not invalid_result[0]:
        print("[PASS] Invalid parameters correctly rejected\n")
    else:
        print("[FAIL] Invalid parameters were not rejected\n")
        return False
    
    # Generate a challenge
    print("3. Generating Challenge Question...")
    print("   Category: Logic")
    print("   Difficulty: Intermediate")
    print("   Programme: General Science")
    print("   Concept: Logical reasoning\n")
    
    result = await gemini_generator.generate_challenge(
        category="Logic",
        difficulty="Intermediate",
        programme="General Science",
        concept="Logical reasoning"
    )
    
    print_result(result)
    
    if result["success"]:
        print("\n" + "=" * 80)
        print("  ALL TESTS PASSED!")
        print("=" * 80)
        print("\nThe Gemini integration is working correctly!")
        print("\nNext steps:")
        print("1. Start the backend server: python -m uvicorn app.main:app --reload")
        print("2. Test the API endpoint with:")
        print("   POST http://localhost:8000/api/v1/challenges/generate-challenge")
        print("   Body: {")
        print('       "category": "Logic",')
        print('       "difficulty": "Intermediate",')
        print('       "programme": "General Science"')
        print("   }")
        return True
    else:
        print("\n" + "=" * 80)
        print("  TEST FAILED")
        print("=" * 80)
        return False


def main():
    """Main test entry point."""
    try:
        success = asyncio.run(test_gemini_integration())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
