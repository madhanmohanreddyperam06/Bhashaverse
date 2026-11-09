"""
BhashaVerse 2.0 - Configuration & Constants
Provides application settings, supported languages metadata, categories, paths, and security configurations.
"""

from pathlib import Path
import os
from typing import Dict, Any, List, Optional

# Base Directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_DB_PATH = DATA_DIR / "bhashaverse.db"

# Application Metadata
APP_NAME = "Bhashaverse"
APP_TAGLINE = "Preserve India's Cultural Wisdom - One Proverb at a time"
APP_MISSION = (
    "A community-driven multilingual platform designed to collect, preserve, "
    "organize, and explore traditional Indian proverbs, folk sayings, idioms, "
    "and cultural expressions to empower NLP research, open datasets, and future AI models."
)
APP_VERSION = "2.0.0"

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
        "sample": "മിന്നുന്നതെല്ലാം പൊன்னല്ല."
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

# Quick lookup mappings
for _lang in SUPPORTED_LANGUAGES:
    _lang["is_rtl"] = _lang.get("direction") == "rtl"

LANGUAGE_NAMES = [lang["name"] for lang in SUPPORTED_LANGUAGES]
LANGUAGE_BY_NAME = {lang["name"]: lang for lang in SUPPORTED_LANGUAGES}
LANGUAGE_BY_CODE = {lang["code"]: lang for lang in SUPPORTED_LANGUAGES}
LANGUAGE_MAP_BY_NAME = LANGUAGE_BY_NAME
LANGUAGE_MAP_BY_CODE = LANGUAGE_BY_CODE
LANGUAGE_CODES = [lang["code"] for lang in SUPPORTED_LANGUAGES]

# Proverb Categories
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

# Moderation Workflow Statuses
STATUS_PENDING = "pending"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"
VALID_STATUSES = {STATUS_PENDING, STATUS_APPROVED, STATUS_REJECTED}

# Input Validation Lengths
PROVERB_MIN_LEN = 3
PROVERB_MAX_LEN = 1000
MEANING_MIN_LEN = 5
MEANING_MAX_LEN = 2000
TRANSLATION_MAX_LEN = 1000
CONTEXT_MAX_LEN = 2500
NAME_MAX_LEN = 100
EMAIL_MAX_LEN = 120

# Pagination Settings
DEFAULT_PAGE_SIZE = 12

def get_db_path() -> Path:
    """
    Get the SQLite database path. Checks:
    1. Streamlit secrets (if available and configured)
    2. Environment variable BHASHAVERSE_DB_PATH
    3. Default data/bhashaverse.db
    """
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "BHASHAVERSE_DB_PATH" in st.secrets:
            return Path(st.secrets["BHASHAVERSE_DB_PATH"]).resolve()
    except Exception:
        pass

    env_path = os.getenv("BHASHAVERSE_DB_PATH")
    if env_path:
        return Path(env_path).resolve()

    return DEFAULT_DB_PATH


def get_moderator_key() -> str:
    """
    Get the secret key required for moderator dashboard access.
    Checks:
    1. Streamlit secrets ('MODERATOR_KEY' or 'moderator_key')
    2. Environment variable MODERATOR_KEY
    3. Default fallback for local testing
    """
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            if "MODERATOR_KEY" in st.secrets:
                return str(st.secrets["MODERATOR_KEY"]).strip()
            if "moderator_key" in st.secrets:
                return str(st.secrets["moderator_key"]).strip()
    except Exception:
        pass

    env_key = os.getenv("MODERATOR_KEY")
    if env_key:
        return env_key.strip()

    # Fallback default key for local offline testing (documented in .env.example)
    return "bhashaverse_maintainer_2026"
