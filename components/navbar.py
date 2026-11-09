"""
Bhashaverse - Navbar & CSS Loader Component
Permanent Dark Theme.
"""

from pathlib import Path
import streamlit as st
from config import BASE_DIR, APP_NAME, APP_TAGLINE


def load_css() -> None:
    """Read and inject assets/styles.css into the Streamlit app (Permanent Dark Mode)."""
    css_path = BASE_DIR / "assets" / "styles.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


def render_header(title: str, subtitle: str = "", badge_text: str = "") -> None:
    """Render theme-aware page title header."""
    load_css()
    badge_html = f"<span class='bv-badge bv-badge-lang' style='margin-left: 0.75rem; vertical-align: middle;'>{badge_text}</span>" if badge_text else ""
    subtitle_html = f"<p style='color: var(--bv-muted); font-size: 0.95rem; margin: 0.25rem 0 0 0;'>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f"""
        <div style="margin-bottom: 1.25rem; border-bottom: 1px solid var(--bv-border); padding-bottom: 0.5rem;">
            <h1 style="color: var(--bv-text); margin: 0; font-size: 2rem; font-weight: 700;">
                {title} {badge_html}
            </h1>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True
    )
