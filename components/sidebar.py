"""
BhashaVerse - Sidebar Component
Renders sidebar brand identity, live status, language overview, and quick links.
Theme-adaptive for both Light and Dark modes.
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
        # Brand logo & title
        st.markdown(
            f"""
            <div style="padding: 0.5rem 0 0.75rem 0; border-bottom: 1px solid var(--bv-border); margin-bottom: 0.75rem;">
                <h2 style="color: var(--bv-text); margin: 0; font-size: 1.35rem; font-weight: 700;">📜 {APP_NAME}</h2>
                <div style="color: var(--bv-primary); font-size: 0.78rem; font-weight: 600; margin-top: 0.2rem; font-style: italic;">
                    "{APP_TAGLINE}"
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Quick live stats
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

        # Navigation links if not on chatbot page
        if not is_chatbot_page:
            if st.button("🤖 Back to Chatbot", type="primary", use_container_width=True, key="sidebar_home_btn"):
                st.switch_page("app.py")

        # Chatbot Controls (when on home/chatbot page)
        if is_chatbot_page:
            st.markdown("### ⚙️ Chat Settings")

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

        # Language badges
        langs_html = " ".join([
            f"<span style='display: inline-block; background: var(--bv-surface); border: 1px solid var(--bv-border); color: var(--bv-text); padding: 2px 6px; border-radius: 4px; font-size: 0.72rem; margin: 2px;'>{lang['name']} ({lang['native_name']})</span>"
            for lang in SUPPORTED_LANGUAGES
        ])
        st.markdown(f"<div style='margin-top: 0.75rem; margin-bottom: 0.5rem;'>{langs_html}</div>", unsafe_allow_html=True)

    return chatbot_settings
