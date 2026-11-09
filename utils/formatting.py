"""
BhashaVerse 2.0 - Formatting & Display Helpers
Provides date formatting, text truncation, safe HTML escaping, and CSS styling utilities.
"""

import html
from datetime import datetime
from typing import Optional


def sanitize_text(text: Optional[str]) -> str:
    """Escape HTML characters to prevent XSS injection in custom HTML renderers."""
    if not text:
        return ""
    return html.escape(str(text))


def format_iso_date(iso_str: Optional[str], include_time: bool = False) -> str:
    """Format an ISO 8601 date string into human-readable representation."""
    if not iso_str:
        return "Unknown"
    try:
        clean_str = iso_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_str)
        if include_time:
            return dt.strftime("%d %b %Y, %H:%M UTC")
        return dt.strftime("%d %b %Y")
    except Exception:
        return str(iso_str)[:10]


def truncate_text(text: Optional[str], max_chars: int = 150) -> str:
    """Truncate text gracefully with ellipsis if length exceeds threshold."""
    if not text:
        return ""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "..."
