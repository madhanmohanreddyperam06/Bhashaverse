"""
Bhashaverse - Analytics & Dataset Export Dashboard
Provides live SQLite-driven statistical analysis, visual charts, and open dataset exports.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Analytics & Datasets | Bhashaverse",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from database import get_statistics, export_proverbs
from components.navbar import render_header
from components.sidebar import render_sidebar
from components.metric_cards import render_metric_cards
from utils.export_utils import generate_csv_export, generate_json_export, get_export_filename

render_header(
    title="Corpus Analytics & Exports",
    subtitle="Live SQLite database statistics, linguistic distribution, and open research dataset downloads"
)
render_sidebar()

# Live statistics
stats = get_statistics()

# Top Metric Cards (inside bordered containers)
st.subheader("Corpus Overview", divider="red")
render_metric_cards(stats)

# Moderation Pipeline
total = stats.get("total_submissions", 0)
approved = stats.get("approved_count", 0)
pending = stats.get("pending_count", 0)
rejected = stats.get("rejected_count", 0)

with st.container(border=True):
    st.subheader("Moderation Pipeline Status")
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.metric("Total Submissions", f"{total:,}")
    with col_s2:
        st.metric("Approved Corpus", f"{approved:,}")
    with col_s3:
        st.metric("Pending Review", f"{pending:,}")
    with col_s4:
        st.metric("Rejected Submissions", f"{rejected:,}")

# Visual Charts
st.subheader("Distribution Analytics", divider="red")
col_chart1, col_chart2 = st.columns(2)

# 1. Language Distribution Chart
lang_dist = stats.get("language_distribution", {})
with col_chart1:
    with st.container(border=True):
        st.subheader("Proverbs by Language")
        if lang_dist:
            if isinstance(lang_dist, dict):
                df_lang = pd.DataFrame([{"language": k, "count": v} for k, v in lang_dist.items()])
            else:
                df_lang = pd.DataFrame(lang_dist)
            fig_lang = px.bar(
                df_lang,
                x="language",
                y="count",
                text="count",
                labels={"language": "Language", "count": "Proverbs"},
                color_discrete_sequence=["#FF4B4B"]
            )
            fig_lang.update_layout(
                showlegend=False,
                margin=dict(l=10, r=10, t=10, b=30),
                xaxis_title="",
                yaxis_title="Count",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#FAFAFA")
            )
            st.plotly_chart(fig_lang, use_container_width=True, theme="streamlit")
        else:
            st.info("No approved proverbs available.")

# 2. Category Distribution Donut Chart
cat_dist = stats.get("category_distribution", {})
with col_chart2:
    with st.container(border=True):
        st.subheader("Thematic Categories")
        if cat_dist:
            if isinstance(cat_dist, dict):
                df_cat = pd.DataFrame([{"category": k, "count": v} for k, v in cat_dist.items()])
            else:
                df_cat = pd.DataFrame(cat_dist)
            fig_cat = px.pie(
                df_cat,
                values="count",
                names="category",
                hole=0.45,
                color_discrete_sequence=px.colors.sequential.Reds_r
            )
            fig_cat.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#FAFAFA")
            )
            st.plotly_chart(fig_cat, use_container_width=True, theme="streamlit")
        else:
            st.info("No category data available.")

# Dataset Export Section
st.subheader("Open Dataset Downloads", divider="red")
with st.container(border=True):
    export_data = export_proverbs(status="approved", include_private=False)
    st.markdown(
        f"Download the verified, human-moderated cultural corpus of **{len(export_data)}** approved proverbs. "
        "UTF-8 encoded with BOM support for seamless analysis in Excel, Pandas, or NLP pipelines."
    )

    exp_col1, exp_col2 = st.columns(2)
    with exp_col1:
        csv_bytes = generate_csv_export(export_data, is_maintainer=False)
        st.download_button(
            label=f"Download CSV Corpus ({len(export_data)} records)",
            data=csv_bytes,
            file_name=get_export_filename("bhashaverse_corpus", "csv"),
            mime="text/csv",
            type="primary",
            use_container_width=True
        )

    with exp_col2:
        json_str = generate_json_export(export_data, is_maintainer=False)
        st.download_button(
            label=f"Download JSON Corpus ({len(export_data)} records)",
            data=json_str,
            file_name=get_export_filename("bhashaverse_corpus", "json"),
            mime="application/json",
            use_container_width=True
        )
