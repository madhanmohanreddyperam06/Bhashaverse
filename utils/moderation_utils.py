"""
BhashaVerse 2.0 - Moderation Security & Utilities
Provides secure moderator passkey verification using constant-time comparison,
session authentication helpers, and moderation action wrappers.
"""

import hmac
from typing import Any
from config import get_moderator_key


def verify_moderator_key(provided_key: str) -> bool:
    """
    Validate moderator secret key using timing-attack resistant comparison.
    Never exposes credentials in logs or output.
    """
    if not provided_key:
        return False
    expected_key = get_moderator_key()
    return hmac.compare_digest(provided_key.strip(), expected_key.strip())


def is_moderator_authenticated(session_state: Any) -> bool:
    """Check if the current Streamlit session has an active authenticated moderator."""
    return bool(session_state.get("is_moderator_authenticated", False))


def authenticate_moderator(session_state: Any, provided_key: str) -> bool:
    """Attempt authentication and set session state flag on success."""
    if verify_moderator_key(provided_key):
        session_state["is_moderator_authenticated"] = True
        return True
    return False


def logout_moderator(session_state: Any) -> None:
    """Clear moderator authentication from session state."""
    session_state["is_moderator_authenticated"] = False
