"""
BhashaVerse 2.0 - Add Proverb / Contribution Form
Enables users to submit folk proverbs in native regional scripts.
"""

import streamlit as st

st.set_page_config(
    page_title="Contribute a Proverb | BhashaVerse 2.0",
    page_icon="✍️",
    layout="wide"
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

render_header(title="✍️ Contribute a Proverb")
render_sidebar()

# Submission Form
with st.form("proverb_submission_form", clear_on_submit=False):
    col_lang, col_cat = st.columns([1, 1])

    with col_lang:
        selected_language = st.selectbox(
            "Language *",
            options=LANGUAGE_NAMES,
            index=0
        )
        lang_meta = LANGUAGE_BY_NAME.get(selected_language, {})

    with col_cat:
        selected_category = st.selectbox(
            "Category",
            options=CATEGORIES,
            index=0
        )

    # Native proverb text
    proverb_text = st.text_area(
        f"Proverb in {selected_language} *",
        placeholder=f"Enter native text (e.g., {lang_meta.get('sample')})",
        height=80
    )

    # English Translation (Optional)
    english_translation = st.text_area(
        "English Translation (Optional)",
        placeholder="Literal or idiomatic translation...",
        height=65
    )

    # Meaning (Required)
    meaning = st.text_area(
        "Meaning *",
        placeholder="Explain what the proverb means...",
        height=80
    )

    # Cultural Context (Optional)
    cultural_context = st.text_area(
        "Cultural Context (Optional)",
        placeholder="Origin, usage, or historical context...",
        height=75
    )

    col_name, col_email = st.columns([1, 1])
    with col_name:
        contributor_name = st.text_input(
            "Contributor Name (Optional)",
            placeholder="Your name or leave blank for Anonymous"
        )
    with col_email:
        contributor_email = st.text_input(
            "Email (Optional)",
            placeholder="Kept private"
        )

    terms_confirmed = st.checkbox(
        "I have permission to share this proverb under the open-source MIT license. *",
        value=False
    )

    submitted = st.form_submit_button("🚀 Submit Proverb", type="primary", use_container_width=True)

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
        st.error(f"⚠️ {validation_result}")
    else:
        try:
            new_record = add_proverb(validation_result)
            st.success("🎉 Your proverb has been submitted successfully and is awaiting review.")
            st.info(
                f"**UUID:** `{new_record.get('submission_uuid')}`  \n"
                f"**Language:** {new_record.get('language')} ({new_record.get('language_code')})  \n"
                f"**Status:** Pending Review"
            )
        except Exception as e:
            st.error(f"❌ Error: {e}")

render_footer()
