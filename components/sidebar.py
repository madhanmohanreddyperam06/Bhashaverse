"""
Bhashaverse - Sidebar Component
Permanent Dark Theme.
Renders brand identity at the top of the sidebar, followed by navigation, chatbot settings, and author credits.
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
        # Title and Sub-heading at the very top (Clean UI, Monochromatic, No Colors)
        st.subheader(f"🌿 {APP_NAME}")
        st.caption(f'"{APP_TAGLINE}"')
        st.divider()

        # Page Navigation Links below Title
        st.page_link("app.py", label="Home")
        st.page_link("pages/1_Explore_Proverbs.py", label="Explore Proverbs")
        st.page_link("pages/2_Add_Proverb.py", label="Add Proverb")
        st.page_link("pages/4_Moderation.py", label="Moderation")
        st.page_link("pages/5_About.py", label="About")

        st.divider()

        # Chatbot Controls (when on home/chatbot page)
        if is_chatbot_page:
            st.caption("CHAT SETTINGS")

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

            if st.button("Clear Conversation", use_container_width=True, key="sidebar_clear_chat"):
                st.session_state["chat_messages"] = []
                st.rerun()

            st.divider()

        # Footer attribution at the very bottom of sidebar
        st.caption("Designed & Developed by Madhan Mohan Reddy Peram")
        st.caption("Built with Streamlit v1.67.0")

    return chatbot_settings
