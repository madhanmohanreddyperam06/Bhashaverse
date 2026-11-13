"""
Bhashaverse - Explore Proverbs
Browse, search, and filter the approved multilingual Indian proverb corpus.
"""

import math
import streamlit as st

st.set_page_config(
    page_title="Explore Proverbs | Bhashaverse",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from config import LANGUAGE_NAMES, CATEGORIES, DEFAULT_PAGE_SIZE
from database import get_approved_proverbs
from components.navbar import render_header
from components.sidebar import render_sidebar
from components.proverb_card import render_proverb_card
from components.footer import render_footer
from utils.export_utils import generate_csv_export, generate_json_export, get_export_filename

render_header(
    title="Explore Proverbs",
    subtitle="Search, filter, and discover cultural wisdom across 10 Indian regional languages"
)
render_sidebar()

# Search & Filters in an official bordered container
with st.container(border=True):
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

# Status header & Export Actions
res_col1, res_col2 = st.columns([0.7, 0.3])
with res_col1:
    st.caption(f"Showing **{len(proverbs)}** of **{total_count}** proverbs (Page **{current_page}** of **{total_pages}**)")

with res_col2:
    if total_count > 0:
        c_csv, c_json = st.columns(2)
        with c_csv:
            csv_data = generate_csv_export(proverbs, is_maintainer=False)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=get_export_filename(f"proverbs_{selected_language.lower()}", "csv"),
                mime="text/csv",
                use_container_width=True
            )
        with c_json:
            json_data = generate_json_export(proverbs, is_maintainer=False)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=get_export_filename(f"proverbs_{selected_language.lower()}", "json"),
                mime="application/json",
                use_container_width=True
            )

# Proverb Grid Display
if proverbs:
    left_col, right_col = st.columns(2)
    for idx, p in enumerate(proverbs):
        target = left_col if idx % 2 == 0 else right_col
        with target:
            render_proverb_card(p)

    # Official Streamlit Pagination Controls
    if total_pages > 1:
        st.divider()
        pag_col1, pag_col2, pag_col3, pag_col4, pag_col5 = st.columns([1, 1, 2, 1, 1])
        with pag_col1:
            if st.button("First", disabled=(current_page == 1), use_container_width=True):
                st.session_state["explore_page"] = 1
                st.rerun()
        with pag_col2:
            if st.button("Previous", disabled=(current_page == 1), use_container_width=True):
                st.session_state["explore_page"] = max(1, current_page - 1)
                st.rerun()
        with pag_col3:
            st.markdown(f"<div style='text-align: center; padding-top: 0.5rem;'>Page <strong>{current_page}</strong> of <strong>{total_pages}</strong></div>", unsafe_allow_html=True)
        with pag_col4:
            if st.button("Next", disabled=(current_page >= total_pages), use_container_width=True):
                st.session_state["explore_page"] = min(total_pages, current_page + 1)
                st.rerun()
        with pag_col5:
            if st.button("Last", disabled=(current_page >= total_pages), use_container_width=True):
                st.session_state["explore_page"] = total_pages
                st.rerun()
else:
    st.info("No proverbs match your criteria. Try adjusting your search query or language filter.")

render_footer()
