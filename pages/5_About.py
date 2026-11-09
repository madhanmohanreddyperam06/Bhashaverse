"""
BhashaVerse 2.0 - About the Project
Mission, linguistic architecture, and open-source contribution guidelines.
"""

import streamlit as st

st.set_page_config(
    page_title="About | BhashaVerse 2.0",
    page_icon="📖",
    layout="wide"
)

from config import (
    APP_NAME,
    APP_TAGLINE,
    SUPPORTED_LANGUAGES
)
from components.navbar import render_header
from components.sidebar import render_sidebar
from components.footer import render_footer

render_header(title="📖 About BhashaVerse")
render_sidebar()

# Mission
st.markdown(
    f"""
    **{APP_NAME}** ({APP_TAGLINE}) is an open-source platform to collect, preserve,
    and explore traditional Indian proverbs across 10 regional languages with native script support.
    """
)

st.markdown("### 🗣️ Supported Languages")
lang_grid = st.columns(2)
for idx, lang in enumerate(SUPPORTED_LANGUAGES):
    col = lang_grid[idx % 2]
    direction_tag = "RTL" if lang.get("direction") == "rtl" else "LTR"
    with col:
        st.markdown(
            f"""
            <div style="background: var(--bv-surface); border: 1px solid var(--bv-border); border-left: 4px solid var(--bv-primary); border-radius: 6px; padding: 0.75rem 1rem; margin-bottom: 0.5rem;">
                <div style="font-weight: 700; color: var(--bv-text); font-size: 1.05rem;">
                    {lang['name']} • <span style="color: var(--bv-primary);">{lang['native_name']}</span>
                </div>
                <div style="font-size: 0.8rem; color: var(--bv-muted);">
                    Script: {lang['script']} • Code: <code>{lang['code']}</code> • {direction_tag}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.divider()

# Quick Start Commands
st.markdown("### 💻 Local Setup")
st.code(
    """git clone https://github.com/your-org/BhashaVerse.git
cd BhashaVerse
pip install -r requirements.txt
streamlit run app.py""",
    language="bash"
)

render_footer()
