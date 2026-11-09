"""
BhashaVerse 2.0 - Metric Cards Component
Renders key platform performance metrics using Streamlit's native components.
Fully theme-responsive across Light and Dark modes.
"""

from typing import Dict, Any
import streamlit as st


def render_metric_cards(stats: Dict[str, Any]) -> None:
    """Render 4 theme-aware metric cards using Streamlit's native st.metric."""
    col1, col2, col3, col4 = st.columns(4)

    approved = stats.get('approved_proverbs') if 'approved_proverbs' in stats else stats.get('approved_count', 0)
    active_langs = stats.get('active_languages') if 'active_languages' in stats else stats.get('active_languages_count', 0)
    pending = stats.get('pending_submissions') if 'pending_submissions' in stats else stats.get('pending_count', 0)
    contributors = stats.get('unique_contributors') if 'unique_contributors' in stats else stats.get('total_contributors', 0)

    with col1:
        st.metric(label="Approved Proverbs", value=f"{approved:,}")

    with col2:
        st.metric(label="Active Languages", value=f"{active_langs} / 10")

    with col3:
        st.metric(label="Pending Review", value=f"{pending:,}")

    with col4:
        st.metric(label="Contributors", value=f"{contributors:,}")
