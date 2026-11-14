"""
Bhashaverse - About the Project
Mission, linguistic architecture, and open-source contribution guidelines.
"""

import streamlit as st

st.set_page_config(
    page_title="About | Bhashaverse",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import Frontend.utils.windows_patch  # Suppress harmless Windows asyncio disconnect warning
from Frontend.config import (
    APP_NAME,
    APP_TAGLINE,
    SUPPORTED_LANGUAGES
)
from Frontend.components.navbar import render_header
from Frontend.components.sidebar import render_sidebar

render_header(
    title="About Bhashaverse",
    subtitle=f"{APP_NAME} — {APP_TAGLINE}"
)
render_sidebar()

# Platform Mission
with st.container(border=True):
    st.subheader("Platform Mission", divider="red")
    st.markdown(
        f"""
        **{APP_NAME}** is an open-source digital humanities and cultural preservation platform. 
        It is dedicated to collecting, organizing, and exploring traditional Indian proverbs, folk sayings 
        (*lokoktiyan / samethalu / pazhamozhigal*), and idioms across regional languages with authentic native script fidelity.
        
        By creating a human-verified, structured multilingual corpus, Bhashaverse empowers Natural Language Processing (NLP) research, 
        cultural AI alignment, and cross-lingual understanding for future generations.
        """
    )

# Supported Languages Showcase
st.subheader("Supported Regional Languages", divider="red")
lang_grid = st.columns(2)
for idx, lang in enumerate(SUPPORTED_LANGUAGES):
    col = lang_grid[idx % 2]
    direction_tag = "RTL (Right-to-Left)" if lang.get("direction") == "rtl" else "LTR (Left-to-Right)"
    with col:
        with st.container(border=True):
            st.markdown(f"### {lang['name']} &nbsp;·&nbsp; :red[{lang['native_name']}]")
            st.caption(f"**Script:** {lang['script']} &nbsp;·&nbsp; **Code:** `{lang['code']}` &nbsp;·&nbsp; **Text Direction:** {direction_tag}")
            st.markdown(f"> *Sample: {lang['sample']}*")

# Architecture Showcase: FastAPI + Streamlit
st.subheader("System Architecture", divider="red")
with st.container(border=True):
    st.markdown(
        """
        - **Backend:** High-performance **FastAPI** REST backend (`/api`) powering search, filtering, moderation, analytics, and RAG grounding.
        - **Frontend:** Responsive, theme-aware **Streamlit** client running in permanent Dark Mode with Times New Roman typography.
        - **Corpus Storage:** Thread-safe **SQLite** with Write-Ahead Logging (WAL) and UTF-8 script fidelity.
        - **Cultural AI:** Multi-model Retrieval-Augmented Generation (RAG) supporting **Ollama**, **Gemini**, **Groq**, **OpenAI**, and an intelligent **Offline Corpus Engine**.
        """
    )

# Local Setup & Contribution
st.subheader("Open Source & Local Setup", divider="red")
with st.container(border=True):
    st.markdown("Bhashaverse is 100% open-source under the MIT license. You can clone and run it locally with Python:")
    st.code(
        """git clone https://github.com/madhanmohanreddyperam06/Bhashaverse.git
cd Bhashaverse
pip install -r requirements.txt

# Run both FastAPI backend and Streamlit frontend concurrently:
python run.py
""",
        language="bash"
    )
