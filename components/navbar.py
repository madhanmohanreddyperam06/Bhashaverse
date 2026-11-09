"""
Bhashaverse - Navbar & CSS Loader Component
Loads styling and renders top branding and navigational context.
Supports explicit Dark Mode and Light Mode switching.
"""

from pathlib import Path
import streamlit as st
from config import BASE_DIR, APP_NAME, APP_TAGLINE


def load_css() -> None:
    """Read and inject assets/styles.css into the Streamlit app with theme support."""
    css_path = BASE_DIR / "assets" / "styles.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

    is_dark = st.session_state.get("dark_mode", True)
    if is_dark:
        dark_css = """
        <style>
        html, body, [data-testid="stAppViewContainer"], .stApp {
            background-color: #0E1117 !important;
            color: #FAFAFA !important;
        }
        [data-testid="stSidebar"], section[data-testid="stSidebar"] {
            background-color: #161B22 !important;
            color: #FAFAFA !important;
            border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
        .bv-landing-hero {
            background: #161B22 !important;
            border-color: rgba(255, 255, 255, 0.12) !important;
            border-top: 4px solid #FF4B4B !important;
        }
        .bv-landing-title {
            color: #FAFAFA !important;
        }
        .bv-card, .bv-lang-card {
            background: #161B22 !important;
            border-color: rgba(255, 255, 255, 0.12) !important;
            color: #FAFAFA !important;
        }
        .bv-proverb-text, .bv-meaning, .bv-lang-name-native {
            color: #FAFAFA !important;
        }
        .stChatMessage {
            background-color: #161B22 !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 8px !important;
        }
        [data-testid="stChatInput"] {
            background-color: #161B22 !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 10px !important;
        }
        [data-testid="stChatInput"] textarea {
            color: #FAFAFA !important;
            background-color: transparent !important;
        }
        div[data-testid="stMetricValue"] {
            color: #FAFAFA !important;
        }
        </style>
        """
        st.markdown(dark_css, unsafe_allow_html=True)
    else:
        light_css = """
        <style>
        html, body, [data-testid="stAppViewContainer"], .stApp {
            background-color: #FFFFFF !important;
            color: #31333F !important;
        }
        [data-testid="stSidebar"], section[data-testid="stSidebar"] {
            background-color: #F8F9FA !important;
            color: #31333F !important;
            border-right: 1px solid rgba(0, 0, 0, 0.08) !important;
        }
        .bv-landing-hero {
            background: #F8F9FA !important;
            border-color: rgba(0, 0, 0, 0.1) !important;
            border-top: 4px solid #FF4B4B !important;
        }
        .bv-landing-title {
            color: #1F2937 !important;
        }
        .bv-card, .bv-lang-card {
            background: #F8F9FA !important;
            border-color: rgba(0, 0, 0, 0.1) !important;
            color: #31333F !important;
        }
        .bv-proverb-text, .bv-meaning, .bv-lang-name-native {
            color: #1F2937 !important;
        }
        .stChatMessage {
            background-color: #F8F9FA !important;
            border: 1px solid rgba(0, 0, 0, 0.08) !important;
            border-radius: 8px !important;
        }
        [data-testid="stChatInput"] {
            background-color: #FFFFFF !important;
            border: 1px solid rgba(0, 0, 0, 0.2) !important;
            border-radius: 10px !important;
        }
        [data-testid="stChatInput"] textarea {
            color: #31333F !important;
            background-color: transparent !important;
        }
        </style>
        """
        st.markdown(light_css, unsafe_allow_html=True)


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
