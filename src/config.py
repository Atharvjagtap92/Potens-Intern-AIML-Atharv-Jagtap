import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Base paths
SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
EVAL_DIR = PROJECT_ROOT / "eval"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
EVAL_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Server Configuration
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
LOG_LEVEL_STR = os.getenv("LOG_LEVEL", "INFO").upper()

# Map log level string to logging constants
LOG_LEVEL = getattr(logging, LOG_LEVEL_STR, logging.INFO)

# Vector Store Path
VECTOR_STORE_PATH = PROJECT_ROOT / "vector_store.json"

def configure_logging(logger_name: str = "potens_rag") -> logging.Logger:
    """Configures structured application logging to both console and a log file."""
    logger = logging.getLogger(logger_name)
    logger.setLevel(LOG_LEVEL)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(name)s:%(filename)s:%(lineno)d] - %(message)s'
        )
        
        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File Handler
        log_file = LOGS_DIR / "app.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
    return logger

logger = configure_logging()

def get_gemini_client():
    """Initializes and returns the Google Generative AI client."""
    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY environment variable is not set. API calls will fail.")
        return None
    
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    return genai
