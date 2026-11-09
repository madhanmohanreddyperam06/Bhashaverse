"""
Tests for BhashaVerse 2.0 Dataset Export.
Verifies UTF-8 BOM encoding for CSV, JSON formatting, privacy guarantees,
and preservation of Indian regional scripts.
"""

import json
from utils.export_utils import (
    generate_csv_export,
    generate_json_export,
    sanitize_records_for_public,
    PUBLIC_EXPORT_FIELDS
)


SAMPLE_RECORDS = [
    {
        "id": 1,
        "submission_uuid": "uuid-123",
        "proverb": "ఆవలిస్తే పేగులు లెక్కపెట్టే రకం.",
        "language": "Telugu",
        "language_code": "te",
        "english_translation": "Counts intestines when you yawn.",
        "meaning": "Exceptionally perceptive individual.",
        "cultural_context": "Telugu colloquial assembly idiom.",
        "category": "Wisdom",
        "contributor_name": "Srinivas",
        "contributor_email": "private_email@example.com",
        "status": "approved",
        "rejection_reason": None,
        "created_at": "2026-11-09T10:00:00Z"
    },
    {
        "id": 2,
        "submission_uuid": "uuid-456",
        "proverb": "ڈوبتے کو تنکے کا سہارا۔",
        "language": "Urdu",
        "language_code": "ur",
        "english_translation": "A straw is a lifeline to a drowning man.",
        "meaning": "Even slight help brings hope in distress.",
        "cultural_context": "Hindustani literary idiom.",
        "category": "Life Lessons",
        "contributor_name": "Tariq",
        "contributor_email": "tariq_private@example.com",
        "status": "approved",
        "rejection_reason": None,
        "created_at": "2026-11-09T11:00:00Z"
    }
]


def test_sanitize_records_for_public():
    """Verify that sensitive columns like email and uuid are stripped."""
    sanitized = sanitize_records_for_public(SAMPLE_RECORDS)
    assert len(sanitized) == 2
    for r in sanitized:
        assert "contributor_email" not in r
        assert "submission_uuid" not in r
        assert "status" not in r
        assert "rejection_reason" not in r
        for field in PUBLIC_EXPORT_FIELDS:
            assert field in r


def test_generate_csv_export_utf8_bom():
    """Verify CSV export is encoded with UTF-8 BOM and preserves Indian scripts."""
    csv_bytes = generate_csv_export(SAMPLE_RECORDS, is_maintainer=False)
    # Check for UTF-8 BOM prefix (\xef\xbb\xbf)
    assert csv_bytes.startswith(b"\xef\xbb\xbf")

    # Decode as utf-8-sig
    csv_text = csv_bytes.decode("utf-8-sig")
    assert "ఆవలిస్తే పేగులు లెక్కపెట్టే రకం." in csv_text
    assert "ڈوبتے کو تنکے کا سہارا۔" in csv_text
    assert "private_email@example.com" not in csv_text


def test_generate_csv_export_maintainer():
    """Verify maintainer CSV export contains full fields."""
    csv_bytes = generate_csv_export(SAMPLE_RECORDS, is_maintainer=True)
    csv_text = csv_bytes.decode("utf-8-sig")
    assert "private_email@example.com" in csv_text
    assert "submission_uuid" in csv_text


def test_generate_json_export():
    """Verify JSON export contains non-escaped Unicode characters."""
    json_str = generate_json_export(SAMPLE_RECORDS, is_maintainer=False)
    assert "ఆవలిస్తే పేగులు లెక్కపెట్టే రకం." in json_str
    assert "ڈوبتے کو تنکے کا سہارا۔" in json_str
    assert "private_email@example.com" not in json_str

    parsed = json.loads(json_str)
    assert len(parsed) == 2
    assert parsed[0]["language"] == "Telugu"
    assert parsed[1]["language"] == "Urdu"
