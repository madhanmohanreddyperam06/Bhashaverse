"""
Tests for BhashaVerse 2.0 Moderation Access Control and Utilities.
Verifies constant-time key validation, session state management, and unauthorized protection.
"""

from utils.moderation_utils import (
    verify_moderator_key,
    is_moderator_authenticated,
    authenticate_moderator,
    logout_moderator
)
from config import get_moderator_key


def test_verify_moderator_key():
    """Verify correct key passes and incorrect key fails."""
    correct_key = get_moderator_key()
    assert verify_moderator_key(correct_key) is True
    assert verify_moderator_key(f"  {correct_key}  ") is True
    assert verify_moderator_key("wrong_password") is False
    assert verify_moderator_key("") is False


def test_session_state_moderation():
    """Verify authentication state transitions."""
    session_mock = {}
    assert is_moderator_authenticated(session_mock) is False

    # Attempt with wrong key
    success = authenticate_moderator(session_mock, "wrong_key")
    assert success is False
    assert is_moderator_authenticated(session_mock) is False

    # Attempt with correct key
    correct_key = get_moderator_key()
    success = authenticate_moderator(session_mock, correct_key)
    assert success is True
    assert is_moderator_authenticated(session_mock) is True

    # Logout
    logout_moderator(session_mock)
    assert is_moderator_authenticated(session_mock) is False
