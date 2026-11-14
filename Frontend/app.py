"""
Bhashaverse - Cultural Wisdom AI Platform
Streamlit Frontend Application Entrypoint
"""

import streamlit as st

st.set_page_config(
    page_title="Bhashaverse",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply Windows asyncio silence patch immediately
import Frontend.utils.windows_patch  # Suppress harmless Windows asyncio WinError 10054 on browser disconnect

# Ensure SQLite schema and seed proverbs exist on startup (critical for fresh container/cloud deployments)
try:
    from Backend.database import ensure_db_initialized
    ensure_db_initialized()
except Exception:
    pass

from Frontend.config import APP_NAME, APP_TAGLINE
from Frontend.api_client import api_client
from Frontend.components.navbar import load_css
from Frontend.components.sidebar import render_sidebar

# Render sidebar navigation and settings
sidebar_settings = render_sidebar(is_chatbot_page=True)

# Load theme CSS
load_css()

# Heading & sub-heading fully left to the page (No Card, No Quotes)
st.title(f"🌿 {APP_NAME}")
st.caption(APP_TAGLINE)

# Chat Session State (Empty by default - no placeholder messages)
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []

# Clear any legacy assistant greeting if present
if len(st.session_state.get("chat_messages", [])) == 1 and st.session_state["chat_messages"][0].get("role") == "assistant":
    st.session_state["chat_messages"] = []

# Render conversation history (only visible when user submits queries)
for msg in st.session_state["chat_messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat Input Bar
user_query = st.chat_input("Ask about proverbs, meanings, or cultural advice...")

if user_query:
    st.session_state["chat_messages"].append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Searching cultural corpus..."):
            response_text = api_client.chat(
                query=user_query,
                language_filter=sidebar_settings.get("language"),
                engine_choice=sidebar_settings.get("engine", "Auto-Detect"),
                custom_api_key=sidebar_settings.get("api_key")
            )
            st.markdown(response_text)

    st.session_state["chat_messages"].append({"role": "assistant", "content": response_text})

