"""
Bhashaverse - Metric Cards Component
Renders key platform metrics using official Streamlit bordered containers and st.metric.
"""

from typing import Dict, Any
import streamlit as st


def render_metric_cards(stats: Dict[str, Any]) -> None:
    """Render 4 theme-aware metric cards using Streamlit's native st.metric inside bordered containers."""
    col1, col2, col3, col4 = st.columns(4)

    approved = stats.get('approved_proverbs', stats.get('approved_count', 0))
    active_langs = stats.get('active_languages', stats.get('active_languages_count', 0))
    pending = stats.get('pending_submissions', stats.get('pending_count', 0))
    contributors = stats.get('unique_contributors', stats.get('total_contributors', 0))

    with col1:
        with st.container(border=True):
            st.metric(label="Approved Proverbs", value=f"{approved:,}")

    with col2:
        with st.container(border=True):
            st.metric(label="Active Languages", value=f"{active_langs} / 10")

    with col3:
        with st.container(border=True):
            st.metric(label="Pending Review", value=f"{pending:,}")

    with col4:
        with st.container(border=True):
            st.metric(label="Contributors", value=f"{contributors:,}")
