"""
BhashaVerse 2.0 - Submission & Data Validation
Ensures data integrity, required fields enforcement, length constraints,
email format validation, category verification, and duplicate prevention.
"""

import re
from typing import Dict, Any, Tuple, Optional, Union
from pathlib import Path

from config import (
    LANGUAGE_NAMES,
    CATEGORIES,
    PROVERB_MIN_LEN,
    PROVERB_MAX_LEN,
    MEANING_MIN_LEN,
    MEANING_MAX_LEN,
    TRANSLATION_MAX_LEN,
    CONTEXT_MAX_LEN,
    NAME_MAX_LEN,
    EMAIL_MAX_LEN
)
from database import check_duplicate_proverb


EMAIL_REGEX = re.compile(r"^[\w\.\+\-]+@[a-zA-Z0-9\-]+(\.[a-zA-Z0-9\-]+)+$")


def validate_email_format(email: str) -> bool:
    """Check if email string conforms to standard email format."""
    if not email:
        return True
    return bool(EMAIL_REGEX.match(email.strip()))


def validate_proverb_submission(
    form_data: Dict[str, Any],
    check_duplicates: bool = True,
    db_path: Optional[Union[str, Path]] = None
) -> Tuple[bool, Union[Dict[str, Any], str]]:
    """
    Validate a proverb contribution submission.
    Returns:
        (True, cleaned_data_dict) on success, or
        (False, error_message_str) on validation failure.
    """
    proverb = (form_data.get("proverb") or "").strip()
    language = (form_data.get("language") or "").strip()
    meaning = (form_data.get("meaning") or "").strip()
    english_translation = (form_data.get("english_translation") or "").strip()
    cultural_context = (form_data.get("cultural_context") or "").strip()
    category = (form_data.get("category") or "Other").strip()
    contributor_name = (form_data.get("contributor_name") or "Anonymous").strip()
    contributor_email = (form_data.get("contributor_email") or "").strip()
    terms_confirmed = form_data.get("terms_confirmed", False)

    # 1. Terms and permission confirmation
    if not terms_confirmed:
        return False, "You must confirm that you have permission to share this proverb and cultural knowledge."

    # 2. Proverb required & length
    if not proverb:
        return False, "Proverb text is required."
    if len(proverb) < PROVERB_MIN_LEN:
        return False, f"Proverb must be at least {PROVERB_MIN_LEN} characters long."
    if len(proverb) > PROVERB_MAX_LEN:
        return False, f"Proverb must not exceed {PROVERB_MAX_LEN} characters."

    # 3. Language validation
    if not language:
        return False, "Please select a language."
    if language not in LANGUAGE_NAMES:
        return False, f"Unsupported language '{language}'. Please select from the supported languages."

    # 4. Meaning required & length
    if not meaning:
        return False, "Meaning / Explanation is required."
    if len(meaning) < MEANING_MIN_LEN:
        return False, f"Meaning must be at least {MEANING_MIN_LEN} characters long."
    if len(meaning) > MEANING_MAX_LEN:
        return False, f"Meaning must not exceed {MEANING_MAX_LEN} characters."

    # 5. Optional fields length validation
    if english_translation and len(english_translation) > TRANSLATION_MAX_LEN:
        return False, f"English translation must not exceed {TRANSLATION_MAX_LEN} characters."

    if cultural_context and len(cultural_context) > CONTEXT_MAX_LEN:
        return False, f"Cultural context must not exceed {CONTEXT_MAX_LEN} characters."

    if contributor_name and len(contributor_name) > NAME_MAX_LEN:
        return False, f"Contributor name must not exceed {NAME_MAX_LEN} characters."

    # 6. Category validation
    if category not in CATEGORIES:
        category = "Other"

    # 7. Contributor email validation (optional)
    if contributor_email:
        if len(contributor_email) > EMAIL_MAX_LEN:
            return False, f"Email address must not exceed {EMAIL_MAX_LEN} characters."
        if not validate_email_format(contributor_email):
            return False, "Please provide a valid email address (e.g. user@example.com)."

    # 8. Duplicate check
    if check_duplicates and check_duplicate_proverb(proverb, language, db_path=db_path):
        return False, f"This proverb has already been contributed for {language}. Thank you!"

    cleaned_data = {
        "proverb": proverb,
        "language": language,
        "meaning": meaning,
        "english_translation": english_translation or None,
        "cultural_context": cultural_context or None,
        "category": category,
        "contributor_name": contributor_name or "Anonymous",
        "contributor_email": contributor_email or None,
        "status": "pending"
    }

    return True, cleaned_data
