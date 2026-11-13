"""
Bhashaverse - Add Proverb / Contribution Form
Enables users to submit folk proverbs in native regional scripts using official Streamlit components.
"""

import streamlit as st

st.set_page_config(
    page_title="Contribute a Proverb | Bhashaverse",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from config import (
    LANGUAGE_NAMES,
    LANGUAGE_BY_NAME,
    CATEGORIES
)
from database import add_proverb
from utils.validation import validate_proverb_submission
from components.navbar import render_header
from components.sidebar import render_sidebar
from components.footer import render_footer

render_header(
    title="Contribute a Proverb",
    subtitle="Submit traditional folk sayings, idioms, and generational wisdom in regional scripts"
)
render_sidebar()

with st.container(border=True):
    with st.form("proverb_submission_form", clear_on_submit=False):
        st.subheader("1. Linguistic & Thematic Details", divider="red")
        col_lang, col_cat = st.columns(2)

        with col_lang:
            selected_language = st.selectbox(
                "Language *",
                options=LANGUAGE_NAMES,
                index=0,
                help="Select one of the 10 supported regional Indian languages."
            )
            lang_meta = LANGUAGE_BY_NAME.get(selected_language, {})

        with col_cat:
            selected_category = st.selectbox(
                "Thematic Category *",
                options=CATEGORIES,
                index=0,
                help="Select the theme that best fits the proverb."
            )

        # Native proverb text
        proverb_text = st.text_area(
            f"Proverb in {selected_language} *",
            placeholder=f"Enter native text (e.g., {lang_meta.get('sample')})",
            height=90,
            help="Enter the original proverb in its native regional Unicode script."
        )

        # English Translation (Optional)
        english_translation = st.text_area(
            "English Translation (Optional)",
            placeholder="Literal or idiomatic English translation...",
            height=70,
            help="Supplementary English translation for researchers and general readers."
        )

        st.subheader("2. Meaning & Cultural Context", divider="red")

        # Meaning (Required)
        meaning = st.text_area(
            "Meaning & Moral Lesson *",
            placeholder="Explain the metaphorical meaning or advice conveyed by this proverb...",
            height=90,
            help="Detailed explanation of the proverb's wisdom and teaching."
        )

        # Cultural Context (Optional)
        cultural_context = st.text_area(
            "Cultural & Historical Context (Optional)",
            placeholder="Origin story, agrarian relevance, festive usage, or historical background...",
            height=80,
            help="Optional folklore, historical background, or specific regional usage."
        )

        st.subheader("3. Attribution & Agreement", divider="red")
        col_name, col_email = st.columns(2)
        with col_name:
            contributor_name = st.text_input(
                "Contributor Name (Optional)",
                placeholder="Leave blank for Anonymous",
                help="Attributed on public proverb cards and open-source exports."
            )
        with col_email:
            contributor_email = st.text_input(
                "Email Address (Optional)",
                placeholder="Kept strictly private",
                help="Never displayed publicly or included in dataset downloads."
            )

        terms_confirmed = st.checkbox(
            "I confirm that I have permission to share this traditional proverb under the open-source MIT license. *",
            value=False
        )

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Submit Proverb for Review", type="primary", use_container_width=True)

if submitted:
    submission_data = {
        "proverb": proverb_text,
        "language": selected_language,
        "meaning": meaning,
        "english_translation": english_translation,
        "cultural_context": cultural_context,
        "category": selected_category,
        "contributor_name": contributor_name,
        "contributor_email": contributor_email,
        "terms_confirmed": terms_confirmed
    }

    is_valid, validation_result = validate_proverb_submission(
        submission_data,
        check_duplicates=True
    )

    if not is_valid:
        st.error(validation_result)
    else:
        try:
            new_record = add_proverb(validation_result)
            st.success("Thank you! Your proverb has been submitted successfully and is awaiting community review.")
            with st.container(border=True):
                st.subheader("Submission Receipt")
                st.markdown(f"**UUID:** `{new_record.get('submission_uuid')}`")
                st.markdown(f"**Language:** {new_record.get('language')} (`{new_record.get('language_code')}`)")
                st.markdown(f"**Status:** :orange[Pending Review]")
        except Exception as e:
            st.error(f"Database error: {e}")

render_footer()
