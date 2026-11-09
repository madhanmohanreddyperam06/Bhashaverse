"""
BhashaVerse 2.0 - Language & Script Utilities
Handles Indian script recognition, Unicode range detection, text direction (LTR/RTL),
and language metadata helpers.
"""

from typing import Dict, Any, Optional, List
from config import SUPPORTED_LANGUAGES, LANGUAGE_BY_NAME, LANGUAGE_BY_CODE, LANGUAGE_NAMES


# Unicode script code point blocks for supported Indian languages
SCRIPT_UNICODE_RANGES = {
    "Devanagari": (0x0900, 0x097F),  # Hindi, Marathi
    "Bengali": (0x0980, 0x09FF),     # Bengali
    "Gujarati": (0x0A80, 0x0AFF),    # Gujarati
    "Odia": (0x0B00, 0x0B7F),        # Odia
    "Tamil": (0x0B80, 0x0BFF),       # Tamil
    "Telugu": (0x0C00, 0x0C7F),      # Telugu
    "Kannada": (0x0C80, 0x0CFF),     # Kannada
    "Malayalam": (0x0D00, 0x0D7F),   # Malayalam
    "Arabic": (0x0600, 0x06FF),      # Urdu / Perso-Arabic
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


def detect_script(text: str) -> Optional[str]:
    """
    Detect the predominant Indian script of the provided text by analyzing Unicode code points.
    Returns script name (e.g. 'Telugu', 'Devanagari', 'Arabic') or None.
    """
    if not text:
        return None

    counts: Dict[str, int] = {script: 0 for script in SCRIPT_UNICODE_RANGES}
    for char in text:
        cp = ord(char)
        for script, (start, end) in SCRIPT_UNICODE_RANGES.items():
            if start <= cp <= end:
                counts[script] += 1
                break

    best_script, best_count = max(counts.items(), key=lambda item: item[1])
    return best_script if best_count > 0 else None


def get_all_language_names() -> List[str]:
    """List of all supported language English names."""
    return list(LANGUAGE_NAMES)


def get_language_dropdown_options() -> List[str]:
    """List of language options for dropdown menus."""
    return [lang["name"] for lang in SUPPORTED_LANGUAGES]
