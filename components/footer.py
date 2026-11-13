"""
Bhashaverse - Footer Component
Renders the standardized minimal footer using official Streamlit components.
"""

import streamlit as st


def render_footer() -> None:
    """Render clean, official Streamlit footer."""
    st.divider()
    st.caption("Designed & Developed by Madhan Mohan Reddy Peram")
    st.caption("Built with Streamlit v1.67.0")
