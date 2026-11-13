"""
Bhashaverse - Cultural Wisdom AI Platform
"""

import streamlit as st

st.set_page_config(
    page_title="Bhashaverse",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded"
)

from config import APP_NAME, APP_TAGLINE
from database import init_db
from utils.chatbot_utils import generate_chat_response
from components.navbar import load_css
from components.sidebar import render_sidebar

# Initialize database
init_db(seed_defaults=True)

# Render sidebar navigation and settings
sidebar_settings = render_sidebar(is_chatbot_page=True)

# Load theme CSS
load_css()

# Professional Hero Card for Header & Sub-header
st.markdown(
    f"""
    <div class="bv-hero-card">
        <div class="bv-hero-left">
            <div class="bv-hero-title">📜 {APP_NAME}</div>
            <div class="bv-hero-subtitle">"{APP_TAGLINE}"</div>
        </div>
        <div class="bv-hero-right">
            <span class="bv-hero-tag">10 Regional Languages</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Chat Session State (Empty by default - no placeholder messages)
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []

# Clear any legacy assistant greeting if present
if len(st.session_state.get("chat_messages", [])) == 1 and st.session_state["chat_messages"][0].get("role") == "assistant":
    st.session_state["chat_messages"] = []

# Render conversation history (only visible when user submits queries)
for msg in st.session_state["chat_messages"]:
    avatar = "👤" if msg["role"] == "user" else "📜"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Chat Input Bar
user_query = st.chat_input("Ask about proverbs, meanings, or cultural advice...")

if user_query:
    st.session_state["chat_messages"].append({"role": "user", "content": user_query})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_query)

    with st.chat_message("assistant", avatar="📜"):
        with st.spinner("Searching cultural corpus..."):
            response_text = generate_chat_response(
                query=user_query,
                language_filter=sidebar_settings.get("language"),
                engine_choice=sidebar_settings.get("engine", "Auto-Detect"),
                custom_api_key=sidebar_settings.get("api_key")
            )
            st.markdown(response_text)

    st.session_state["chat_messages"].append({"role": "assistant", "content": response_text})
