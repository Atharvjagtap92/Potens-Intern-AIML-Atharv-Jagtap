import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

api_key = os.getenv("GEMINI_API_KEY", "")

try:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    
    print("Listing available models for your API key...")
    models = list(genai.list_models())
    if not models:
        print("[WARNING] No models returned for this key!")
    else:
        print("[SUCCESS] Models found:")
        for m in models:
            print(f" - {m.name} (Supports: {m.supported_generation_methods})")
except Exception as e:
    print(f"[FAILED] Error listing models: {e}")
