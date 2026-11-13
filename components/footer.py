"""
Bhashaverse - Footer Component
Renders the standardized minimal footer using official Streamlit components.
"""

import streamlit as st
from config import APP_NAME, APP_VERSION


def render_footer() -> None:
    """Render clean, official Streamlit footer."""
    st.divider()
    st.caption(f"{APP_NAME} v{APP_VERSION} · Open-Source MIT License · Preserving India's Linguistic Heritage")
