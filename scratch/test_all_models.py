import sys
from pathlib import Path
from dotenv import load_dotenv

# Set paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

import src.config as config

def test_models():
    client = config.get_gemini_client()
    if not client:
        print("[ERROR] Gemini client failed to initialize.")
        return
        
    candidate_models = [
        "gemini-2.0-flash-lite",
        "gemini-2.5-pro",
        "gemini-3.5-flash",
        "gemini-pro-latest",
        "gemini-flash-latest"
    ]
    
    print("Testing candidate models for active quota...\n")
    
    for model_name in candidate_models:
        print(f"Testing model: '{model_name}'...")
        try:
            model = client.GenerativeModel(model_name)
            # Make a tiny request with a short timeout to see if it succeeds
            response = model.generate_content("Say 'Hi' and nothing else.", request_options={"timeout": 6.0})
            print(f"  [SUCCESS] Model '{model_name}' is ACTIVE and has quota! Response: '{response.text.strip()}'")
        except Exception as e:
            # Check if it is a 429 (quota) or 404 (not found) or other error
            err_msg = str(e)
            print(f"  [ERROR] Model '{model_name}' failed with exception:\n  {err_msg}")
        print()

if __name__ == "__main__":
    test_models()
