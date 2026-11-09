"""
BhashaVerse 2.0 - Explore Proverbs
Browse, search, and filter the approved multilingual Indian proverb corpus.
"""

import math
import streamlit as st

st.set_page_config(
    page_title="Explore Proverbs | BhashaVerse 2.0",
    page_icon="🔍",
    layout="wide"
)

from config import LANGUAGE_NAMES, CATEGORIES, DEFAULT_PAGE_SIZE
from database import get_approved_proverbs
from components.navbar import render_header
from components.sidebar import render_sidebar
from components.proverb_card import render_proverb_card
from components.footer import render_footer
from utils.export_utils import generate_csv_export, generate_json_export, get_export_filename

render_header(title="🔍 Explore Proverbs")
render_sidebar()

# Search and Filter Controls
filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([2.5, 1.2, 1.2, 1.1])

with filter_col1:
    search_query = st.text_input(
        "Search",
        placeholder="Search proverb, translation, or meaning...",
        key="explore_search"
    )

with filter_col2:
    selected_language = st.selectbox(
        "Language",
        options=["All"] + LANGUAGE_NAMES,
        index=0,
        key="explore_lang"
    )

with filter_col3:
    selected_category = st.selectbox(
        "Category",
        options=["All"] + CATEGORIES,
        index=0,
        key="explore_cat"
    )

with filter_col4:
    sort_option = st.selectbox(
        "Sort",
        options=["Newest First", "Oldest First", "Alphabetical"],
        index=0,
        key="explore_sort"
    )

sort_map = {
    "Newest First": "newest",
    "Oldest First": "oldest",
    "Alphabetical": "alphabetical"
}
sort_key = sort_map.get(sort_option, "newest")

# Initialize session page state
if "explore_page" not in st.session_state:
    st.session_state["explore_page"] = 1

# Reset page to 1 if filters change
filter_fingerprint = f"{search_query}_{selected_language}_{selected_category}_{sort_key}"
if st.session_state.get("last_filter_fingerprint") != filter_fingerprint:
    st.session_state["explore_page"] = 1
    st.session_state["last_filter_fingerprint"] = filter_fingerprint

current_page = st.session_state["explore_page"]

# Fetch results from database
proverbs, total_count = get_approved_proverbs(
    query=search_query,
    language=selected_language,
    category=selected_category,
    sort_by=sort_key,
    page=current_page,
    per_page=DEFAULT_PAGE_SIZE
)

total_pages = max(1, math.ceil(total_count / DEFAULT_PAGE_SIZE))

# Results count & Export buttons
res_col1, res_col2 = st.columns([2, 1])
with res_col1:
    st.markdown(
        f"<p style='color: var(--bv-muted); font-size: 0.9rem; margin-top: 0.5rem;'>"
        f"Showing <strong>{len(proverbs)}</strong> of <strong>{total_count}</strong> proverbs (Page {current_page} of {total_pages})"
        f"</p>",
        unsafe_allow_html=True
    )

with res_col2:
    if total_count > 0:
        c_csv, c_json = st.columns(2)
        with c_csv:
            csv_data = generate_csv_export(proverbs, is_maintainer=False)
            st.download_button(
                label="📥 Page CSV",
                data=csv_data,
                file_name=get_export_filename(f"proverbs_{selected_language.lower()}", "csv"),
                mime="text/csv",
                use_container_width=True
            )
        with c_json:
            json_data = generate_json_export(proverbs, is_maintainer=False)
            st.download_button(
                label="📥 Page JSON",
                data=json_data,
                file_name=get_export_filename(f"proverbs_{selected_language.lower()}", "json"),
                mime="application/json",
                use_container_width=True
            )

st.divider()

# Proverb Grid Display
if proverbs:
    left_col, right_col = st.columns(2)
    for idx, p in enumerate(proverbs):
        target = left_col if idx % 2 == 0 else right_col
        with target:
            render_proverb_card(p)

    # Pagination Controls
    if total_pages > 1:
        st.markdown("<br>", unsafe_allow_html=True)
        pag_col1, pag_col2, pag_col3, pag_col4, pag_col5 = st.columns([1, 1, 2, 1, 1])
        with pag_col1:
            if st.button("⏮️ First", disabled=(current_page == 1), use_container_width=True):
                st.session_state["explore_page"] = 1
                st.rerun()
        with pag_col2:
            if st.button("◀️ Prev", disabled=(current_page == 1), use_container_width=True):
                st.session_state["explore_page"] = max(1, current_page - 1)
                st.rerun()
        with pag_col3:
            st.markdown(
                f"<div style='text-align: center; padding-top: 0.4rem; font-weight: 600; color: var(--bv-primary);'>Page {current_page} / {total_pages}</div>",
                unsafe_allow_html=True
            )
        with pag_col4:
            if st.button("Next ▶️", disabled=(current_page >= total_pages), use_container_width=True):
                st.session_state["explore_page"] = min(total_pages, current_page + 1)
                st.rerun()
        with pag_col5:
            if st.button("Last ⏭️", disabled=(current_page >= total_pages), use_container_width=True):
                st.session_state["explore_page"] = total_pages
                st.rerun()
else:
    st.info("No proverbs match your criteria.")

render_footer()
