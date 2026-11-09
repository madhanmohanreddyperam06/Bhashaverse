"""
BhashaVerse 2.0 - Proverb Card Component
Renders individual proverbs with native scripts, RTL text alignment for Urdu,
language and category badges, cultural context, and contributor attribution.
"""

from typing import Dict, Any
import streamlit as st

from utils.formatting import sanitize_text, format_iso_date
from utils.language_utils import is_rtl, get_display_label


def render_proverb_card(proverb_data: Dict[str, Any], show_actions: bool = False) -> None:
    """Render a single proverb card with full cultural metadata and styling."""
    proverb_text = sanitize_text(proverb_data.get("proverb", ""))
    language = proverb_data.get("language", "Unknown")
    display_lang = sanitize_text(get_display_label(language))
    category = sanitize_text(proverb_data.get("category", "Other"))
    translation = sanitize_text(proverb_data.get("english_translation", ""))
    meaning = sanitize_text(proverb_data.get("meaning", ""))
    cultural_context = sanitize_text(proverb_data.get("cultural_context", ""))
    contributor = sanitize_text(proverb_data.get("contributor_name", "Anonymous"))
    date_str = format_iso_date(proverb_data.get("created_at"))

    rtl_class = "rtl" if is_rtl(language) else ""

    translation_html = (
        f"""<div class="bv-translation">"{translation}"</div>"""
        if translation else ""
    )

    context_html = (
        f"""
        <div class="bv-context">
            <strong>🏛️ Cultural Context:</strong> {cultural_context}
        </div>
        """
        if cultural_context else ""
    )

    card_html = f"""
    <div class="bv-card">
        <div class="bv-card-header">
            <span class="bv-badge bv-badge-lang">{display_lang}</span>
            <span class="bv-badge bv-badge-cat">{category}</span>
        </div>
        <div class="bv-proverb-text {rtl_class}">
            {proverb_text}
        </div>
        {translation_html}
        <div class="bv-meaning">
            <strong>💡 Meaning:</strong> {meaning}
        </div>
        {context_html}
        <div class="bv-card-footer">
            <span>👤 Contributed by <strong>{contributor}</strong></span>
            <span>📅 {date_str}</span>
        </div>
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)
