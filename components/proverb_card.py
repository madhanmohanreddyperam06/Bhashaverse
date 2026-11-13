"""
Bhashaverse - Proverb Card Component
Renders individual proverbs using official Streamlit containers and components.
"""

from typing import Dict, Any
import streamlit as st

from utils.formatting import sanitize_text, format_iso_date
from utils.language_utils import is_rtl, get_display_label


def render_proverb_card(proverb_data: Dict[str, Any], show_actions: bool = False) -> None:
    """Render a single proverb card using official Streamlit bordered container."""
    proverb_text = sanitize_text(proverb_data.get("proverb", ""))
    language = proverb_data.get("language", "Unknown")
    display_lang = sanitize_text(get_display_label(language))
    category = sanitize_text(proverb_data.get("category", "Other"))
    translation = sanitize_text(proverb_data.get("english_translation", ""))
    meaning = sanitize_text(proverb_data.get("meaning", ""))
    cultural_context = sanitize_text(proverb_data.get("cultural_context", ""))
    contributor = sanitize_text(proverb_data.get("contributor_name", "Anonymous"))
    date_str = format_iso_date(proverb_data.get("created_at"))

    with st.container(border=True):
        col_meta, col_date = st.columns([0.68, 0.32])
        with col_meta:
            st.markdown(f":red[**{display_lang}**] &nbsp;·&nbsp; :gray[{category}]")
        with col_date:
            st.caption(f"📅 {date_str}")

        # Proverb text
        if is_rtl(language):
            st.markdown(f"<div class='rtl-text'>{proverb_text}</div>", unsafe_allow_html=True)
        else:
            st.subheader(proverb_text)

        # English Translation
        if translation:
            st.markdown(f'> *"{translation}"*')

        # Meaning
        st.markdown(f"**💡 Meaning:** {meaning}")

        # Cultural Context
        if cultural_context:
            with st.expander("🏛️ Cultural Context", expanded=False):
                st.write(cultural_context)

        # Contributor Attribution
        st.caption(f"👤 Contributed by **{contributor}**")
