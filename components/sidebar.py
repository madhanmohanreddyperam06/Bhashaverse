"""
Bhashaverse - Sidebar Component
Permanent Dark Theme.
Renders brand identity at the top of the sidebar, followed by navigation, chatbot settings, and live stats.
"""

from typing import Dict, Any, Optional
import streamlit as st
from config import APP_NAME, APP_TAGLINE, SUPPORTED_LANGUAGES, LANGUAGE_NAMES
from database import get_statistics


def render_sidebar(is_chatbot_page: bool = False) -> Dict[str, Any]:
    """
    Render permanent dark-themed sidebar across all Streamlit pages.
    Title is positioned at the top of the sidebar.
    Returns chatbot settings if on the chatbot page.
    """
    chatbot_settings: Dict[str, Any] = {
        "engine": "Auto-Detect",
        "api_key": None,
        "language": None
    }

    with st.sidebar:
        # Title at the very top of sidebar
        st.markdown(
            f"""
            <div style="padding: 0.25rem 0 0.6rem 0; border-bottom: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 0.75rem;">
                <h2 style="color: #FAFAFA; margin: 0; font-size: 1.4rem; font-weight: 700;">📜 {APP_NAME}</h2>
                <div style="color: #FF4B4B; font-size: 0.8rem; font-weight: 600; margin-top: 0.25rem; font-style: italic;">
                    "{APP_TAGLINE}"
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Page Navigation Links below Title
        st.page_link("app.py", label="Home (Chatbot)", icon="🤖")
        st.page_link("pages/1_Explore_Proverbs.py", label="Explore Proverbs", icon="🔍")
        st.page_link("pages/2_Add_Proverb.py", label="Add Proverb", icon="✍️")
        st.page_link("pages/3_Dashboard.py", label="Dashboard & Export", icon="📊")
        st.page_link("pages/4_Moderation.py", label="Moderation", icon="🛡️")
        st.page_link("pages/5_About.py", label="About", icon="ℹ️")

        st.divider()

        # Chatbot Controls (when on home/chatbot page)
        if is_chatbot_page:
            st.markdown("<p style='font-size: 0.82rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #9E9E9E; margin-bottom: 0.35rem;'>Chat Settings</p>", unsafe_allow_html=True)

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
                <div style="background: #161B22; border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 6px; padding: 0.5rem 0.75rem; margin-bottom: 0.75rem; font-size: 0.82rem; color: #FAFAFA;">
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
            f"<span style='display: inline-block; background: #161B22; border: 1px solid rgba(255, 255, 255, 0.12); color: #FAFAFA; padding: 2px 6px; border-radius: 4px; font-size: 0.72rem; margin: 2px;'>{lang['name']} ({lang['native_name']})</span>"
            for lang in SUPPORTED_LANGUAGES
        ])
        st.markdown(f"<div style='margin-bottom: 0.5rem;'>{langs_html}</div>", unsafe_allow_html=True)

    return chatbot_settings
