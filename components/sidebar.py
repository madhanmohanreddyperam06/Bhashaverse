"""
Bhashaverse - Sidebar Component
Renders sidebar brand identity, theme toggle, navigation links, and live stats.
Fully theme-adaptive for both Light and Dark modes.
"""

from typing import Dict, Any, Optional
import streamlit as st
from config import APP_NAME, APP_TAGLINE, SUPPORTED_LANGUAGES, LANGUAGE_NAMES
from database import get_statistics


def render_sidebar(is_chatbot_page: bool = False) -> Dict[str, Any]:
    """
    Render theme-aware sidebar across all Streamlit pages.
    Returns chatbot settings if on the chatbot page.
    """
    chatbot_settings: Dict[str, Any] = {
        "engine": "Auto-Detect",
        "api_key": None,
        "language": None
    }

    with st.sidebar:
        # Dark Mode Toggle at the top of sidebar
        col_t1, col_t2 = st.columns([2, 1])
        with col_t1:
            st.markdown(
                f"<div style='font-size: 1.2rem; font-weight: 800; color: var(--bv-text); padding-top: 0.2rem;'>📜 {APP_NAME}</div>",
                unsafe_allow_html=True
            )
        with col_t2:
            dark_mode = st.toggle(
                "🌙 Dark",
                value=st.session_state.get("dark_mode", True),
                key="theme_dark_toggle",
                label_visibility="collapsed"
            )
            if dark_mode != st.session_state.get("dark_mode", True):
                st.session_state["dark_mode"] = dark_mode
                st.rerun()

        st.markdown(
            f"""
            <div style="color: #FF4B4B; font-size: 0.78rem; font-weight: 600; font-style: italic; margin-bottom: 0.75rem; border-bottom: 1px solid var(--bv-border); padding-bottom: 0.5rem;">
                "{APP_TAGLINE}"
            </div>
            """,
            unsafe_allow_html=True
        )

        # Navigation Links
        st.markdown("<p style='font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.25rem;'>Navigation</p>", unsafe_allow_html=True)
        st.page_link("app.py", label="Home (Chatbot)", icon="🤖")
        st.page_link("pages/1_Explore_Proverbs.py", label="Explore Proverbs", icon="🔍")
        st.page_link("pages/2_Add_Proverb.py", label="Add Proverb", icon="✍️")
        st.page_link("pages/3_Dashboard.py", label="Dashboard & Export", icon="📊")
        st.page_link("pages/4_Moderation.py", label="Moderation", icon="🛡️")
        st.page_link("pages/5_About.py", label="About", icon="ℹ️")

        st.divider()

        # Chatbot Controls (when on home/chatbot page)
        if is_chatbot_page:
            st.markdown("<p style='font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.25rem;'>Chat Settings</p>", unsafe_allow_html=True)

            engine_choice = st.selectbox(
                "AI Engine",
                options=[
                    "Auto-Detect",
                    "Offline Corpus Engine",
                    "Gemini",
                    "Groq",
                    "OpenAI"
                ],
                index=0,
                key="sidebar_engine_select"
            )

            custom_api_key = st.text_input(
                "API Key (Optional)",
                type="password",
                placeholder="Gemini / Groq / OpenAI...",
                key="sidebar_api_key_input"
            )

            chat_lang_filter = st.selectbox(
                "Language Focus",
                options=["All Languages"] + LANGUAGE_NAMES,
                index=0,
                key="sidebar_lang_filter"
            )
            target_lang = None if chat_lang_filter == "All Languages" else chat_lang_filter

            chatbot_settings = {
                "engine": engine_choice,
                "api_key": custom_api_key.strip() if custom_api_key else None,
                "language": target_lang
            }

            if st.button("🧹 Clear Conversation", use_container_width=True, key="sidebar_clear_chat"):
                st.session_state["chat_messages"] = []
                st.rerun()

            st.divider()

        # Quick Live Stats
        try:
            stats = get_statistics()
            approved = stats.get('approved_proverbs', stats.get('approved_count', 0))
            active_langs = stats.get('active_languages', stats.get('active_languages_count', 0))
            contributors = stats.get('unique_contributors', stats.get('total_contributors', 0))
            st.markdown(
                f"""
                <div style="background: var(--bv-surface); border: 1px solid var(--bv-border); border-radius: 6px; padding: 0.5rem 0.75rem; margin-bottom: 0.75rem; font-size: 0.82rem; color: var(--bv-text);">
                    <div>📚 <strong>Approved:</strong> {approved:,}</div>
                    <div>🗣️ <strong>Languages:</strong> {active_langs} / 10</div>
                    <div>👥 <strong>Contributors:</strong> {contributors:,}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        except Exception:
            pass

        # Language Badges
        langs_html = " ".join([
            f"<span style='display: inline-block; background: var(--bv-surface); border: 1px solid var(--bv-border); color: var(--bv-text); padding: 2px 6px; border-radius: 4px; font-size: 0.72rem; margin: 2px;'>{lang['name']} ({lang['native_name']})</span>"
            for lang in SUPPORTED_LANGUAGES
        ])
        st.markdown(f"<div style='margin-bottom: 0.5rem;'>{langs_html}</div>", unsafe_allow_html=True)

    return chatbot_settings
