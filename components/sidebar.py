"""
Bhashaverse - Sidebar Component
Permanent Dark Theme.
Renders brand identity at the top of the sidebar, followed by navigation, chatbot settings, and live stats.
"""

from typing import Dict, Any, Optional
import streamlit as st
from config import APP_NAME, APP_TAGLINE, LANGUAGE_NAMES


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
        st.page_link("app.py", label="Home")
        st.page_link("pages/1_Explore_Proverbs.py", label="Explore Proverbs")
        st.page_link("pages/2_Add_Proverb.py", label="Add Proverb")
        st.page_link("pages/4_Moderation.py", label="Moderation")
        st.page_link("pages/5_About.py", label="About")

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

    return chatbot_settings
