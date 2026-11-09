"""
Tests for BhashaVerse 2.0 Database Layer.
Verifies SQLite initialization, CRUD, moderation workflows, search,
and flawless Unicode support for all 10 Indian languages.
"""

import os
import tempfile
from pathlib import Path
import pytest

from database import (
    init_db,
    add_proverb,
    check_duplicate_proverb,
    get_proverb_by_id,
    get_proverb_by_uuid,
    get_approved_proverbs,
    get_pending_proverbs,
    get_rejected_proverbs,
    update_proverb,
    approve_proverb,
    reject_proverb,
    restore_proverb_to_pending,
    delete_proverb,
    search_proverbs,
    get_statistics,
    export_proverbs,
    get_moderation_logs,
    STATUS_APPROVED,
    STATUS_PENDING,
    STATUS_REJECTED,
)
from config import SUPPORTED_LANGUAGES


@pytest.fixture
def temp_db():
    """Create an isolated temporary SQLite database for each test."""
    temp_dir = tempfile.mkdtemp()
    db_file = Path(temp_dir) / "test_bhashaverse.db"
    init_db(db_path=db_file, seed_if_empty=False)
    yield db_file
    if db_file.exists():
        try:
            os.remove(db_file)
        except Exception:
            pass


def test_init_db(temp_db):
    """Test that database schema and tables are correctly initialized."""
    stats = get_statistics(db_path=temp_db)
    assert stats["total_submissions"] == 0
    assert stats["approved_proverbs"] == 0
    assert stats["pending_submissions"] == 0


def test_add_and_retrieve_proverb(temp_db):
    """Test inserting a proverb and retrieving it by ID and UUID."""
    record = add_proverb(
        proverb="जल ही जीवन है।",
        language="Hindi",
        language_code="hi",
        meaning="Water is essential for life.",
        english_translation="Water is life.",
        cultural_context="Ancient Indian belief in Pancha Bhuta (five elements).",
        category="Nature",
        contributor_name="Ravi Kumar",
        contributor_email="ravi@example.com",
        db_path=temp_db,
    )
    assert record is not None
    assert record["id"] is not None
    assert record["status"] == STATUS_PENDING
    assert record["proverb"] == "जल ही जीवन है।"
    assert record["contributor_name"] == "Ravi Kumar"
    assert record["contributor_email"] == "ravi@example.com"

    # Fetch by ID
    by_id = get_proverb_by_id(record["id"], db_path=temp_db)
    assert by_id is not None
    assert by_id["submission_uuid"] == record["submission_uuid"]

    # Fetch by UUID
    by_uuid = get_proverb_by_uuid(record["submission_uuid"], db_path=temp_db)
    assert by_uuid is not None
    assert by_uuid["id"] == record["id"]


def test_unicode_all_10_languages(temp_db):
    """
    Test Unicode fidelity for all 10 supported regional languages:
    Hindi, Telugu, Tamil, Bengali, Marathi, Urdu (RTL), Gujarati, Kannada, Malayalam, Odia.
    """
    sample_proverbs = [
        ("Hindi", "hi", "नाच न जाने आँगन टेढ़ा।", "A bad workman blames his tools."),
        ("Telugu", "te", "కుక్క తోక వంకర తీయలేరు.", "A dog's crooked tail cannot be straightened."),
        ("Tamil", "ta", "அகத்தின் அழகு முகத்தில் தெரியும்.", "The face is the mirror of the mind."),
        ("Bengali", "bn", "গাছে কাঁঠাল গোঁফে তেল।", "Counting your chickens before they hatch."),
        ("Marathi", "mr", "सुंठीवाचून खोकला गेला.", "The ailment disappeared without medicine/trouble."),
        ("Urdu", "ur", "ناچ نہ جانے آنگن ٹیڑھا۔", "One who cannot dance blames the courtyard."),
        ("Gujarati", "gu", "ખાડો ખોદે તે પડે.", "He who digs a pit falls into it."),
        ("Kannada", "kn", "ಕೈ ಕೆಸರಾದರೆ ಬಾಯಿ ಮೊಸರು.", "Hard work yields sweet fruits."),
        ("Malayalam", "ml", "ചുമരില്ലാതെ ചിത്രം വരയ്ക്കാനാവില്ല.", "You cannot paint a picture without a wall."),
        ("Odia", "or", "ଅଳ୍ପ ବିଦ୍ୟା ଭୟଙ୍କରୀ।", "A little knowledge is a dangerous thing."),
    ]

    for lang_name, lang_code, text, trans in sample_proverbs:
        rec = add_proverb(
            proverb=text,
            language=lang_name,
            language_code=lang_code,
            meaning="Sample test meaning for Unicode test.",
            english_translation=trans,
            category="Wisdom",
            db_path=temp_db,
        )
        assert rec is not None
        fetched = get_proverb_by_id(rec["id"], db_path=temp_db)
        assert fetched["proverb"] == text
        assert fetched["language"] == lang_name
        assert fetched["language_code"] == lang_code


def test_duplicate_detection(temp_db):
    """Test duplicate detection for identical or space/case-normalized text."""
    add_proverb(
        proverb="अधजल गगरी छलकत जाए।",
        language="Hindi",
        language_code="hi",
        meaning="Shallow knowledge boasts.",
        db_path=temp_db,
    )

    # Identical
    assert check_duplicate_proverb("अधजल गगरी छलकत जाए।", "Hindi", db_path=temp_db) is True
    # Different spacing
    assert check_duplicate_proverb("  अधजल   गगरी   छलकत जाए।  ", "Hindi", db_path=temp_db) is True
    # Different language
    assert check_duplicate_proverb("अधजल गगरी छलकत जाए।", "Telugu", db_path=temp_db) is False


def test_moderation_approval_workflow(temp_db):
    """Test approving a pending submission and logging audit trail."""
    rec = add_proverb(
        proverb="నవ్విపోదురు గాక నాకేటి సిగ్గు.",
        language="Telugu",
        language_code="te",
        meaning="Let them laugh; I have no shame in doing what is right.",
        db_path=temp_db,
    )
    p_id = rec["id"]

    # Initially in pending
    pending = get_pending_proverbs(db_path=temp_db)
    assert any(p["id"] == p_id for p in pending)
    approved = get_approved_proverbs(db_path=temp_db)
    assert not any(p["id"] == p_id for p in approved)

    # Approve
    ok = approve_proverb(p_id, moderator="admin_tester", notes="Verified authentic", db_path=temp_db)
    assert ok is True

    # Check updated status
    updated = get_proverb_by_id(p_id, db_path=temp_db)
    assert updated["status"] == STATUS_APPROVED
    assert updated["moderated_by"] == "admin_tester"

    # Now in approved, no longer in pending
    assert any(p["id"] == p_id for p in get_approved_proverbs(db_path=temp_db))
    assert not any(p["id"] == p_id for p in get_pending_proverbs(db_path=temp_db))

    # Check moderation logs
    logs = get_moderation_logs(proverb_id=p_id, db_path=temp_db)
    assert any(l["action"] == "approved" and l["moderator"] == "admin_tester" for l in logs)


def test_moderation_rejection_workflow(temp_db):
    """Test rejecting a submission with a recorded reason."""
    rec = add_proverb(
        proverb="Random gibberish text",
        language="Hindi",
        language_code="hi",
        meaning="Not a real proverb",
        db_path=temp_db,
    )
    p_id = rec["id"]

    ok = reject_proverb(p_id, reason="Gibberish / Spam", moderator="mod_1", db_path=temp_db)
    assert ok is True

    updated = get_proverb_by_id(p_id, db_path=temp_db)
    assert updated["status"] == STATUS_REJECTED
    assert updated["rejection_reason"] == "Gibberish / Spam"

    # Verify lists
    assert any(p["id"] == p_id for p in get_rejected_proverbs(db_path=temp_db))
    assert not any(p["id"] == p_id for p in get_approved_proverbs(db_path=temp_db))
    assert not any(p["id"] == p_id for p in get_pending_proverbs(db_path=temp_db))

    # Test restoring to pending
    restored = restore_proverb_to_pending(p_id, moderator="mod_1", db_path=temp_db)
    assert restored is True
    assert get_proverb_by_id(p_id, db_path=temp_db)["status"] == STATUS_PENDING


def test_update_proverb(temp_db):
    """Test editing proverb details."""
    rec = add_proverb(
        proverb="ஒன்றுபட்டால் உண்டு வாழ்வு.",
        language="Tamil",
        language_code="ta",
        meaning="Unity gives life.",
        db_path=temp_db,
    )
    p_id = rec["id"]

    updated = update_proverb(
        p_id,
        english_translation="United we stand, divided we fall.",
        meaning="Solidarity ensures survival and prosperity.",
        category="Society",
        moderator="editor_1",
        db_path=temp_db,
    )
    assert updated is True

    record = get_proverb_by_id(p_id, db_path=temp_db)
    assert record["english_translation"] == "United we stand, divided we fall."
    assert record["meaning"] == "Solidarity ensures survival and prosperity."
    assert record["category"] == "Society"


def test_delete_proverb_cascades(temp_db):
    """Test permanently deleting a proverb and foreign key cascade on moderation logs."""
    rec = add_proverb(
        proverb="To be deleted",
        language="Marathi",
        language_code="mr",
        meaning="Temporary",
        db_path=temp_db,
    )
    p_id = rec["id"]

    # Delete
    deleted = delete_proverb(p_id, db_path=temp_db)
    assert deleted is True
    assert get_proverb_by_id(p_id, db_path=temp_db) is None
    # Moderation logs should also be cleared due to ON DELETE CASCADE
    logs = get_moderation_logs(proverb_id=p_id, db_path=temp_db)
    assert len(logs) == 0


def test_search_and_filtering(temp_db):
    """Test search across text, translations, meanings, language, and category filters."""
    p1 = add_proverb(
        proverb="సూర్యునిపై ఉమ్మివేస్తే మన ముఖంపైనే పడుతుంది.",
        language="Telugu",
        language_code="te",
        meaning="Spitting at the sun only soils your own face.",
        english_translation="Do not defame great people.",
        category="Wisdom",
        status=STATUS_APPROVED,
        db_path=temp_db,
    )
    p2 = add_proverb(
        proverb="গাছ লাগাও প্রাণ বাঁচাও।",
        language="Bengali",
        language_code="bn",
        meaning="Plant trees and save lives.",
        english_translation="Save nature.",
        category="Nature",
        status=STATUS_APPROVED,
        db_path=temp_db,
    )
    # A pending proverb should not appear in approved search results
    p3 = add_proverb(
        proverb="Pending proverb not approved",
        language="Telugu",
        language_code="te",
        meaning="Hidden",
        status=STATUS_PENDING,
        db_path=temp_db,
    )

    # Search by text in proverb
    res, count = search_proverbs(query="సూర్యునిపై", db_path=temp_db)
    assert count == 1
    assert res[0]["id"] == p1["id"]

    # Search by English translation
    res, count = search_proverbs(query="Save nature", db_path=temp_db)
    assert count == 1
    assert res[0]["id"] == p2["id"]

    # Filter by language
    res, count = search_proverbs(language="Telugu", db_path=temp_db)
    assert count == 1
    assert res[0]["id"] == p1["id"]

    # Filter by category
    res, count = search_proverbs(category="Nature", db_path=temp_db)
    assert count == 1
    assert res[0]["id"] == p2["id"]

    # Ensure pending proverb is never in approved search
    res, count = search_proverbs(query="Pending proverb", db_path=temp_db)
    assert count == 0


def test_statistics_calculation(temp_db):
    """Test live calculation of dashboard metrics and distribution."""
    # 2 approved Telugu, 1 approved Hindi, 1 pending Gujarati
    add_proverb("Proverb 1", "Telugu", "te", "Meaning 1", status=STATUS_APPROVED, contributor_name="User A", db_path=temp_db)
    add_proverb("Proverb 2", "Telugu", "te", "Meaning 2", status=STATUS_APPROVED, contributor_name="User B", db_path=temp_db)
    add_proverb("Proverb 3", "Hindi", "hi", "Meaning 3", status=STATUS_APPROVED, contributor_name="User A", db_path=temp_db)
    add_proverb("Proverb 4", "Gujarati", "gu", "Meaning 4", status=STATUS_PENDING, contributor_name="User C", db_path=temp_db)

    stats = get_statistics(db_path=temp_db)
    assert stats["total_submissions"] == 4
    assert stats["approved_proverbs"] == 3
    assert stats["pending_submissions"] == 1
    assert stats["active_languages"] == 2  # Telugu and Hindi are approved
    assert stats["language_distribution"]["Telugu"] == 2
    assert stats["language_distribution"]["Hindi"] == 1
    assert stats["unique_contributors"] >= 2


def test_export_proverbs_privacy(temp_db):
    """Verify export includes required metadata but strictly NEVER exposes contributor email."""
    add_proverb(
        proverb="రహస్య పరీక్ష",
        language="Telugu",
        language_code="te",
        meaning="Privacy test",
        contributor_name="Confidential User",
        contributor_email="sensitive_email@test.com",
        status=STATUS_APPROVED,
        db_path=temp_db,
    )

    public_data = export_proverbs(approved_only=True, db_path=temp_db)
    assert len(public_data) == 1
    row = public_data[0]
    assert "contributor_email" not in row
    assert row["contributor_name"] == "Confidential User"
    assert row["proverb"] == "రహస్య పరీక్ష"

    maintainer_data = export_proverbs(approved_only=False, include_maintainer_meta=True, db_path=temp_db)
    assert len(maintainer_data) == 1
    m_row = maintainer_data[0]
    assert "contributor_email" not in m_row
    assert "status" in m_row
