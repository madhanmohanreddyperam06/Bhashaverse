"""
Bhashaverse - Frontend Language & Script Utilities
Handles Indian script recognition, Unicode range detection, and text direction (LTR/RTL).
"""

from typing import Dict, Any, Optional, List
from Frontend.config import SUPPORTED_LANGUAGES, LANGUAGE_BY_NAME, LANGUAGE_BY_CODE, LANGUAGE_NAMES

SCRIPT_UNICODE_RANGES = {
    "Devanagari": (0x0900, 0x097F),
    "Bengali": (0x0980, 0x09FF),
    "Gujarati": (0x0A80, 0x0AFF),
    "Odia": (0x0B00, 0x0B7F),
    "Tamil": (0x0B80, 0x0BFF),
    "Telugu": (0x0C00, 0x0C7F),
    "Kannada": (0x0C80, 0x0CFF),
    "Malayalam": (0x0D00, 0x0D7F),
    "Arabic": (0x0600, 0x06FF),
}


def get_language_info(lang_name_or_code: str) -> Optional[Dict[str, Any]]:
    """Retrieve metadata dict for a language by English name or ISO code."""
    if not lang_name_or_code:
        return None
    name_clean = lang_name_or_code.strip()
    if name_clean in LANGUAGE_BY_NAME:
        return LANGUAGE_BY_NAME[name_clean]
    if name_clean.lower() in LANGUAGE_BY_CODE:
        return LANGUAGE_BY_CODE[name_clean.lower()]
    return None


def is_rtl(lang_name_or_code: str) -> bool:
    """Return True if language text direction is Right-to-Left (e.g. Urdu)."""
    info = get_language_info(lang_name_or_code)
    if info:
        return info.get("direction") == "rtl"
    return str(lang_name_or_code).lower() in ("urdu", "ur")


def get_display_label(lang_name: str) -> str:
    """Return formatted display label, e.g. 'Telugu (తెలుగు)'."""
    info = get_language_info(lang_name)
    if info:
        return info.get("display_label", lang_name)
    return lang_name

