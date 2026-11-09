"""
Bhashaverse - Landing Page & Cultural Wisdom AI Chatbot
Preserve India's Cultural Wisdom - One Proverb at a time.
"""

import streamlit as st

st.set_page_config(
    page_title="Bhashaverse | Cultural Wisdom Platform",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded"
)

from config import APP_NAME, APP_TAGLINE, SUPPORTED_LANGUAGES
from database import init_db, get_statistics
from utils.chatbot_utils import generate_chat_response
from components.navbar import load_css
from components.sidebar import render_sidebar
from components.metric_cards import render_metric_cards
from components.proverb_card import render_proverb_card
from components.footer import render_footer

# Initialize database
init_db(seed_defaults=True)

# Load responsive theme CSS
load_css()

# Default to Chatbot mode
if "app_mode" not in st.session_state:
    st.session_state["app_mode"] = "chatbot"

# Render sidebar with chatbot controls
sidebar_settings = render_sidebar(is_chatbot_page=(st.session_state["app_mode"] == "chatbot"))

# ==========================================
# 1. Landing Page Header (Exact User Spec)
# ==========================================
st.markdown(
    f"""
    <div class="bv-landing-hero">
        <h1 class="bv-landing-title">{APP_NAME}</h1>
        <p class="bv-landing-tagline">"{APP_TAGLINE}"</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Mode Selector Pills / Toggle
mode_col1, mode_col2 = st.columns([3, 1])
with mode_col2:
    selected_mode = st.radio(
        "View Mode",
        options=["🤖 Chatbot", "🏛️ Overview"],
        index=0 if st.session_state["app_mode"] == "chatbot" else 1,
        horizontal=True,
        label_visibility="collapsed",
        key="mode_radio"
    )
    new_mode = "chatbot" if selected_mode == "🤖 Chatbot" else "overview"
    if new_mode != st.session_state["app_mode"]:
        st.session_state["app_mode"] = new_mode
        st.rerun()

# ==========================================
# 2. DEFAULT VIEW: BhashaAI Chatbot
# ==========================================
if st.session_state["app_mode"] == "chatbot":
    # Chat Session State Initialization
    if "chat_messages" not in st.session_state or not st.session_state["chat_messages"]:
        st.session_state["chat_messages"] = [
            {
                "role": "assistant",
                "content": "🙏 **Namaste!** Ask me about proverbs across our 10 supported Indian languages, their meanings, or cross-lingual equivalents."
            }
        ]

    # Quick Suggestion Prompts
    sug_col1, sug_col2, sug_col3 = st.columns(3)
    prompt_to_submit = None

    with sug_col1:
        if st.button("🌾 Nature & Agriculture", use_container_width=True, key="quick_sug_1"):
            prompt_to_submit = "Tell me traditional Indian proverbs about agriculture, rain, and nature."

    with sug_col2:
        if st.button("🔄 Telugu & Hindi Equivalents", use_container_width=True, key="quick_sug_2"):
            prompt_to_submit = "Give me equivalent proverbs in Telugu and Hindi about living within one's means or avoiding pride."

    with sug_col3:
        if st.button("🏛️ Urdu & Tamil Wisdom", use_container_width=True, key="quick_sug_3"):
            prompt_to_submit = "Share meaningful proverbs in Urdu and Tamil about resilience and perseverance."

    # Render Chat History
    for msg in st.session_state["chat_messages"]:
        avatar = "👤" if msg["role"] == "user" else "📜"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # Handle User Input
    user_query = st.chat_input("Ask about proverbs, meanings, or cultural advice...")
    final_prompt = prompt_to_submit or user_query

    if final_prompt:
        st.session_state["chat_messages"].append({"role": "user", "content": final_prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(final_prompt)

        with st.chat_message("assistant", avatar="📜"):
            with st.spinner("Searching cultural corpus..."):
                response_text = generate_chat_response(
                    query=final_prompt,
                    language_filter=sidebar_settings.get("language"),
                    engine_choice=sidebar_settings.get("engine", "Auto-Detect"),
                    custom_api_key=sidebar_settings.get("api_key")
                )
                st.markdown(response_text)

        st.session_state["chat_messages"].append({"role": "assistant", "content": response_text})

# ==========================================
# 3. OVERVIEW VIEW: Quick Stats & Languages
# ==========================================
else:
    stats = get_statistics()

    # Quick Navigation Buttons to Sidebar Features
    c_b1, c_b2, c_b3, c_b4 = st.columns(4)
    with c_b1:
        if st.button("🤖 Return to Chatbot", type="primary", use_container_width=True, key="ov_chat_btn"):
            st.session_state["app_mode"] = "chatbot"
            st.rerun()
    with c_b2:
        if st.button("🔍 Explore Proverbs", use_container_width=True, key="ov_explore_btn"):
            st.switch_page("pages/1_Explore_Proverbs.py")
    with c_b3:
        if st.button("✍️ Add Proverb", use_container_width=True, key="ov_add_btn"):
            st.switch_page("pages/2_Add_Proverb.py")
    with c_b4:
        if st.button("📊 Dashboard & Export", use_container_width=True, key="ov_dash_btn"):
            st.switch_page("pages/3_Dashboard.py")

    st.markdown("<br>", unsafe_allow_html=True)

    # Statistics
    st.markdown("### 📊 Corpus Overview")
    render_metric_cards(stats)

    st.markdown("<br>", unsafe_allow_html=True)

    # 10 Supported Languages Showcase
    st.markdown("### 🗣️ Supported Languages")
    lang_cols = st.columns(5)
    for i, lang in enumerate(SUPPORTED_LANGUAGES):
        col = lang_cols[i % 5]
        with col:
            st.markdown(
                f"""
                <div class="bv-lang-card">
                    <div class="bv-lang-name-native">{lang['native_name']}</div>
                    <div class="bv-lang-name-en">{lang['name']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # Recently Approved Proverbs Section
    st.markdown("### 🌟 Recently Approved Proverbs")
    recent_proverbs = stats.get("recent_proverbs", [])
    if recent_proverbs:
        col_a, col_b = st.columns(2)
        for idx, p in enumerate(recent_proverbs):
            target_col = col_a if idx % 2 == 0 else col_b
            with target_col:
                render_proverb_card(p)
    else:
        st.info("No approved proverbs yet.")

# Footer
render_footer()
