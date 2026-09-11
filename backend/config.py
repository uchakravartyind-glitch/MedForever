import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env if present
load_dotenv(BASE_DIR / ".env")

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
APP_PORT = int(os.getenv("PORT", 8000))
APP_HOST = os.getenv("HOST", "127.0.0.1")

# Runtime memory key storage (for keys entered directly via web UI)
_runtime_keys = {
    "gemini_api_key": GEMINI_API_KEY
}

def get_api_key() -> str:
    """Return currently active Gemini API key (env or runtime)."""
    return _runtime_keys.get("gemini_api_key") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""

def set_runtime_api_key(key: str) -> None:
    """Update active API key at runtime."""
    _runtime_keys["gemini_api_key"] = key.strip()

def has_valid_api_key() -> bool:
    """Check if API key is provided and valid."""
    key = get_api_key()
    return bool(key and len(key) > 10)
