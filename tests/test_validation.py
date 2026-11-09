"""
Tests for BhashaVerse 2.0 Validation Logic.
Verifies required fields, constraints, email formats, categories, and permission checks.
"""

from utils.validation import validate_proverb_submission, validate_email_format


def test_validate_email_format():
    """Verify email format validator."""
    assert validate_email_format("") is True
    assert validate_email_format("test@example.com") is True
    assert validate_email_format("user.name+tag@domain.co.in") is True
    assert validate_email_format("invalid-email") is False
    assert validate_email_format("@missingusername.com") is False
    assert validate_email_format("user@.com") is False


def test_validate_submission_success():
    """Verify valid submission passes validation."""
    valid_data = {
        "proverb": "ఆవలిస్తే పేగులు లెక్కపెట్టే రకం.",
        "language": "Telugu",
        "meaning": "Someone who can deduce thoughts instantly.",
        "english_translation": "Counts intestines when you yawn.",
        "category": "Wisdom",
        "contributor_name": "Srinivas",
        "contributor_email": "srinivas@example.com",
        "terms_confirmed": True
    }
    is_valid, result = validate_proverb_submission(valid_data, check_duplicates=False)
    assert is_valid is True
    assert isinstance(result, dict)
    assert result["proverb"] == valid_data["proverb"]
    assert result["language"] == "Telugu"


def test_validate_submission_missing_terms():
    """Verify missing terms confirmation fails validation."""
    data = {
        "proverb": "अधजल गगरी छलकत जाए।",
        "language": "Hindi",
        "meaning": "Boasting due to lack of deep knowledge.",
        "terms_confirmed": False
    }
    is_valid, msg = validate_proverb_submission(data, check_duplicates=False)
    assert is_valid is False
    assert "permission" in msg.lower()


def test_validate_submission_empty_proverb():
    """Verify empty or short proverb fails validation."""
    data = {
        "proverb": "  ",
        "language": "Hindi",
        "meaning": "Valid meaning for proverb.",
        "terms_confirmed": True
    }
    is_valid, msg = validate_proverb_submission(data, check_duplicates=False)
    assert is_valid is False
    assert "proverb" in msg.lower()


def test_validate_submission_invalid_language():
    """Verify unsupported language fails validation."""
    data = {
        "proverb": "Valid proverb text",
        "language": "Klingon",
        "meaning": "Valid meaning here.",
        "terms_confirmed": True
    }
    is_valid, msg = validate_proverb_submission(data, check_duplicates=False)
    assert is_valid is False
    assert "unsupported language" in msg.lower()


def test_validate_submission_empty_meaning():
    """Verify empty or short meaning fails validation."""
    data = {
        "proverb": "Valid proverb text",
        "language": "Tamil",
        "meaning": "Hi",
        "terms_confirmed": True
    }
    is_valid, msg = validate_proverb_submission(data, check_duplicates=False)
    assert is_valid is False
    assert "meaning" in msg.lower()


def test_validate_submission_invalid_email():
    """Verify invalid email format is flagged."""
    data = {
        "proverb": "Valid proverb text",
        "language": "Odia",
        "meaning": "Valid explanation of the proverb.",
        "contributor_email": "not-an-email",
        "terms_confirmed": True
    }
    is_valid, msg = validate_proverb_submission(data, check_duplicates=False)
    assert is_valid is False
    assert "email" in msg.lower()
