"""
diagnose_models.py — Check DeepSeek API connectivity

Tests that the DeepSeek API key works by making a simple request.
"""
import sys
import httpx
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings

DEEPSEEK_CHAT_URL = "https://api.deepseek.com/v1/chat/completions"


async def check_deepseek():
    """Check DeepSeek API connectivity."""
    print("Checking DeepSeek API configuration...\n")

    if not settings.DEEPSEEK_API_KEY:
        print("[FAIL] DEEPSEEK_API_KEY is not configured in .env file")
        return False

    print(f"[PASS] DEEPSEEK_API_KEY is set")
    print(f"[INFO] Model: {settings.DEEPSEEK_MODEL}")
    print()

    headers = {
        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.DEEPSEEK_MODEL,
        "messages": [
            {"role": "user", "content": "Say 'Hello, DeepSeek!' and nothing else."}
        ],
        "max_tokens": 32,
        "stream": False,
    }

    try:
        import asyncio
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                DEEPSEEK_CHAT_URL,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print(f"Response: {content}")
            print("\n[PASS] DeepSeek API is working correctly!")
            return True
    except httpx.HTTPStatusError as e:
        print(f"\n[FAIL] DeepSeek API HTTP error {e.response.status_code}: {e.response.text}")
        return False
    except Exception as e:
        print(f"\n[FAIL] DeepSeek API error: {e}")
        return False


def main():
    import asyncio
    success = asyncio.run(check_deepseek())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
