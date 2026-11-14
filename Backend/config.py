"""
Bhashaverse - Backend Configuration
Provides server settings, database paths, supported languages, categories, and security parameters.
"""

from pathlib import Path
import os
from typing import Dict, Any, List

# Base Directories (root of repository)
BACKEND_DIR = Path(__file__).resolve().parent
BASE_DIR = BACKEND_DIR.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_DB_PATH = DATA_DIR / "bhashaverse.db"

# Application Metadata
APP_NAME = "Bhashaverse"
APP_TAGLINE = "Preserving Languages. Connecting Cultures. Empowering AI."
APP_VERSION = "2.0.0"

# CORS Origins
CORS_ORIGINS = ["*"]
API_PREFIX = "/api"

# 10 Supported Indian Languages Metadata
SUPPORTED_LANGUAGES: List[Dict[str, Any]] = [
    {
        "name": "Hindi",
        "native_name": "हिन्दी",
        "code": "hi",
        "display_label": "Hindi (हिन्दी)",
        "script": "Devanagari",
        "direction": "ltr",
        "sample": "अधजल गगरी छलकत जाए।"
    },
    {
        "name": "Telugu",
        "native_name": "తెలుగు",
        "code": "te",
        "display_label": "Telugu (తెలుగు)",
        "script": "Telugu",
        "direction": "ltr",
        "sample": "ఆవలిస్తే పేగులు లెక్కపెట్టే రకం."
    },
    {
        "name": "Tamil",
        "native_name": "தமிழ்",
        "code": "ta",
        "display_label": "Tamil (தமிழ்)",
        "script": "Tamil",
        "direction": "ltr",
        "sample": "அகத்தின் அழகு முகத்தில் தெரியும்."
    },
    {
        "name": "Bengali",
        "native_name": "বাংলা",
        "code": "bn",
        "display_label": "Bengali (বাংলা)",
        "script": "Bengali",
        "direction": "ltr",
        "sample": "যত গর্জে তত বর্ষে না।"
    },
    {
        "name": "Marathi",
        "native_name": "मराठी",
        "code": "mr",
        "display_label": "Marathi (मराठी)",
        "script": "Devanagari",
        "direction": "ltr",
        "sample": "शितावरून भाताची परीक्षा."
    },
    {
        "name": "Urdu",
        "native_name": "اردو",
        "code": "ur",
        "display_label": "Urdu (اردو)",
        "script": "Perso-Arabic",
        "direction": "rtl",
        "sample": "ڈوبتے کو تنکے کا سہارا۔"
    },
    {
        "name": "Gujarati",
        "native_name": "ગુજરાતી",
        "code": "gu",
        "display_label": "Gujarati (ગુજરાતી)",
        "script": "Gujarati",
        "direction": "ltr",
        "sample": "ઉતાવળે આંબા ન પાકે."
    },
    {
        "name": "Kannada",
        "native_name": "ಕನ್ನಡ",
        "code": "kn",
        "display_label": "Kannada (ಕನ್ನಡ)",
        "script": "Kannada",
        "direction": "ltr",
        "sample": "ಮಾತು ಬೆಳ್ಳಿ, ಮೌನ ಬಂಗಾರ."
    },
    {
        "name": "Malayalam",
        "native_name": "മലയാളം",
        "code": "ml",
        "display_label": "Malayalam (മലയാളം)",
        "script": "Malayalam",
        "direction": "ltr",
        "sample": "ಮಿನ್ನുന്നതെല്ലാം പൊன்னല്ല."
    },
    {
        "name": "Odia",
        "native_name": "ଓଡ଼ିଆ",
        "code": "or",
        "display_label": "Odia (ଓଡ଼ିଆ)",
        "script": "Odia",
        "direction": "ltr",
        "sample": "ଅଳ୍ପ ବିଦ୍ୟା ଭୟଙ୍କରୀ।"
    },
]

for _lang in SUPPORTED_LANGUAGES:
    _lang["is_rtl"] = _lang.get("direction") == "rtl"

LANGUAGE_NAMES = [lang["name"] for lang in SUPPORTED_LANGUAGES]
LANGUAGE_BY_NAME = {lang["name"]: lang for lang in SUPPORTED_LANGUAGES}
LANGUAGE_BY_CODE = {lang["code"]: lang for lang in SUPPORTED_LANGUAGES}
LANGUAGE_MAP_BY_NAME = LANGUAGE_BY_NAME
LANGUAGE_MAP_BY_CODE = LANGUAGE_BY_CODE
LANGUAGE_CODES = [lang["code"] for lang in SUPPORTED_LANGUAGES]

CATEGORIES: List[str] = [
    "Wisdom",
    "Life Lessons",
    "Relationships",
    "Nature",
    "Agriculture",
    "Family",
    "Society",
    "Education",
    "Morality",
    "Tradition",
    "Other"
]

STATUS_PENDING = "pending"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"
VALID_STATUSES = {STATUS_PENDING, STATUS_APPROVED, STATUS_REJECTED}

PROVERB_MIN_LEN = 3
PROVERB_MAX_LEN = 1000
MEANING_MIN_LEN = 5
MEANING_MAX_LEN = 2000
TRANSLATION_MAX_LEN = 1000
CONTEXT_MAX_LEN = 2500
NAME_MAX_LEN = 100
EMAIL_MAX_LEN = 120

DEFAULT_PAGE_SIZE = 12


def get_db_path() -> Path:
    """Return resolved SQLite DB path from environment or default."""
    env_path = os.getenv("BHASHAVERSE_DB_PATH")
    if env_path:
        return Path(env_path).resolve()
    return DEFAULT_DB_PATH


def get_moderator_key() -> str:
    """Get secret key required for moderator dashboard access."""
    env_key = os.getenv("MODERATOR_KEY")
    if env_key:
        return env_key.strip()
    return "bhashaverse_maintainer_2026"

