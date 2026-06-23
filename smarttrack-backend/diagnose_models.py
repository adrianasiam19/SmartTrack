"""
diagnose_models.py — Check available Gemini models
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import google.generativeai as genai
from app.config import settings

print("Configuring with API key...")
genai.configure(api_key=settings.GEMINI_API_KEY)

print("Listing available models...\n")
try:
    models = genai.list_models()
    for model in models:
        print(f"Model: {model.name}")
        print(f"  Display: {model.display_name}")
        print()
except Exception as e:
    print(f"Error: {e}")
