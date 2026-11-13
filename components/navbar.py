"""
Bhashaverse - Navbar & Header Component
Standardized professional Streamlit header.
"""

from pathlib import Path
import streamlit as st
from config import BASE_DIR, APP_NAME, APP_TAGLINE


def load_css() -> None:
    """Read and inject assets/styles.css into the Streamlit app."""
    css_path = BASE_DIR / "assets" / "styles.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


def render_header(title: str, subtitle: str = "", badge_text: str = "") -> None:
    """Render professional Streamlit native header."""
    load_css()
    if badge_text:
        col_t, col_b = st.columns([0.82, 0.18])
        with col_t:
            st.title(title)
        with col_b:
            st.markdown(
                f"<div style='text-align: right; padding-top: 1rem;'><span class='bv-badge bv-badge-lang'>{badge_text}</span></div>",
                unsafe_allow_html=True
            )
    else:
        st.title(title)

    if subtitle:
        st.caption(subtitle)

    st.divider()
