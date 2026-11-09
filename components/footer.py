"""
BhashaVerse 2.0 - Footer Component
Renders the standardized open-source footer across all pages.
"""

import streamlit as st
from config import APP_NAME, APP_VERSION


def render_footer() -> None:
    """Render clean, minimal footer."""
    st.markdown(
        f"""
        <div class="bv-footer" style="margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #E5E7EB; text-align: center; color: #9CA3AF; font-size: 0.8rem;">
            <span>{APP_NAME} v{APP_VERSION}</span> • <span>MIT License</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
