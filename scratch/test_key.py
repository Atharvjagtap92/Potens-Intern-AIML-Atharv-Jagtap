import os
from pathlib import Path
from dotenv import load_dotenv

# Load env
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

api_key = os.getenv("GEMINI_API_KEY", "")

print(f"Testing API Key: '{api_key[:10]}...{api_key[-5:] if len(api_key) > 5 else ''}'")
print(f"Key length: {len(api_key)} characters")

if not api_key:
    print("[ERROR] GEMINI_API_KEY is empty in your .env file!")
    exit(1)
    
if not api_key.startswith("AIzaSy"):
    print("[WARNING] Standard Gemini API keys from Google AI Studio usually start with 'AIzaSy'.")
    print("          Your key starts with a different prefix. It may be invalid.")

try:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    
    print("\nConnecting to Gemini API...")
    # Attempt a lightweight request to test the key
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # 5 second timeout test
    response = model.generate_content("Say hello", request_options={"timeout": 5.0})
    print("\n[SUCCESS] The Gemini API Key is valid!")
    print(f"Response: '{response.text.strip()}'")
except Exception as e:
    print("\n[FAILED] Gemini API returned an error:")
    print(f"Error type: {type(e).__name__}")
    print(f"Error details: {e}")
