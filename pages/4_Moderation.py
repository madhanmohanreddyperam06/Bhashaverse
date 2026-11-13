"""
Bhashaverse - Maintainer Moderation Dashboard
Restricted-access management interface for community proverbs review,
verification, categorization, edit-before-approval, rejection logging,
and audit trail inspection. Built using official Streamlit UI components.
"""

import streamlit as st

st.set_page_config(
    page_title="Moderation | Bhashaverse",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from config import (
    LANGUAGE_NAMES,
    CATEGORIES
)
from database import (
    get_pending_proverbs,
    get_approved_proverbs,
    get_rejected_proverbs,
    approve_proverb,
    reject_proverb,
    restore_proverb_to_pending,
    update_proverb,
    delete_proverb,
    get_moderation_logs,
    export_proverbs
)
from utils.moderation_utils import (
    is_moderator_authenticated,
    authenticate_moderator,
    logout_moderator
)
from utils.formatting import format_iso_date, sanitize_text
from utils.language_utils import is_rtl, get_display_label
from utils.export_utils import generate_csv_export, generate_json_export, get_export_filename
from components.navbar import render_header
from components.sidebar import render_sidebar

render_header(title="Moderation Console", badge_text="Restricted Access")
render_sidebar()

# ==========================================
# 1. Authentication Gateway
# ==========================================
if not is_moderator_authenticated(st.session_state):
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        with st.container(border=True):
            st.subheader("Maintainer Authentication")
            st.caption("Enter your secure maintainer passcode to unlock moderation tools.")
            with st.form("moderator_login_form"):
                passkey_input = st.text_input(
                    "Passcode",
                    type="password",
                    placeholder="Enter maintainer key..."
                )
                submit_btn = st.form_submit_button("Unlock Console", type="primary", use_container_width=True)

                if submit_btn:
                    if authenticate_moderator(st.session_state, passkey_input):
                        st.success("Authentication successful.")
                        st.rerun()
                    else:
                        st.error("Invalid passcode. Please verify and try again.")

    st.stop()


# ==========================================
# 2. Authenticated Maintainer Toolbar
# ==========================================
top_col1, top_col2 = st.columns([0.8, 0.2])
with top_col1:
    st.markdown("**Maintainer Session Active** &nbsp;·&nbsp; Authorized for review, editing, and audits.")
with top_col2:
    if st.button("Log Out", use_container_width=True):
        logout_moderator(st.session_state)
        st.rerun()

st.divider()

# Fetch active counts
pending_list = get_pending_proverbs()
approved_list = get_approved_proverbs(limit=250)
rejected_list = get_rejected_proverbs()
logs_list = get_moderation_logs(limit=100)

tab_pending, tab_approved, tab_rejected, tab_logs, tab_export = st.tabs([
    f"Pending Review ({len(pending_list)})",
    f"Approved Corpus ({len(approved_list)})",
    f"Rejected Archive ({len(rejected_list)})",
    f"Audit Logs ({len(logs_list)})",
    "Maintainer Export"
])

# ==========================================
# TAB 1: Pending Review
# ==========================================
with tab_pending:
    if not pending_list:
        st.info("The review queue is currently empty. All submissions have been moderated.")
    else:
        for p in pending_list:
            p_id = p["id"]
            lang = p["language"]
            display_lang = get_display_label(lang)

            with st.expander(f"[{display_lang}] #{p_id}: {p['proverb'][:50]}...", expanded=True):
                with st.container(border=True):
                    info_col1, info_col2 = st.columns([0.65, 0.35])

                    with info_col1:
                        if is_rtl(lang):
                            st.markdown(f"<div class='rtl-text'>{sanitize_text(p['proverb'])}</div>", unsafe_allow_html=True)
                        else:
                            st.subheader(sanitize_text(p["proverb"]))

                        if p.get("english_translation"):
                            st.markdown(f'> *"{sanitize_text(p["english_translation"])}"*')

                        st.markdown(f"**Meaning:** {sanitize_text(p['meaning'])}")

                        if p.get("cultural_context"):
                            st.caption(f"**Context:** {sanitize_text(p['cultural_context'])}")

                    with info_col2:
                        with st.container(border=True):
                            st.caption(f"**UUID:** `{p['submission_uuid'][:8]}`")
                            st.caption(f"**Category:** {p['category']}")
                            st.caption(f"**Submitted:** {format_iso_date(p['created_at'])}")
                            st.caption(f"**Contributor:** {sanitize_text(p.get('contributor_name') or 'Anonymous')}")
                            if p.get("contributor_email"):
                                st.caption(f"**Email:** `{sanitize_text(p['contributor_email'])}`")

                # Action Buttons
                action_col1, action_col2, action_col3 = st.columns([1, 1, 1.2])

                with action_col1:
                    if st.button("Approve", key=f"apprv_{p_id}", type="primary", use_container_width=True):
                        if approve_proverb(p_id, moderator="maintainer"):
                            st.success(f"Approved proverb #{p_id}")
                            st.rerun()

                with action_col2:
                    with st.popover("Reject", use_container_width=True):
                        st.caption("Provide reason for rejection:")
                        reject_reason = st.text_input("Reason", placeholder="Duplicate, low quality, inappropriate...", key=f"rej_reason_{p_id}")
                        if st.button("Confirm Rejection", key=f"conf_rej_{p_id}", type="primary", use_container_width=True):
                            if reject_proverb(p_id, reason=reject_reason, moderator="maintainer"):
                                st.rerun()

                with action_col3:
                    with st.popover("Edit & Approve", use_container_width=True):
                        st.caption("Correct text or category before publishing:")
                        edit_proverb = st.text_input("Proverb Text", value=p["proverb"], key=f"edt_prv_{p_id}")
                        edit_trans = st.text_input("Translation", value=p.get("english_translation") or "", key=f"edt_tr_{p_id}")
                        edit_meaning = st.text_area("Meaning", value=p["meaning"], key=f"edt_mn_{p_id}")
                        edit_context = st.text_area("Context", value=p.get("cultural_context") or "", key=f"edt_ctx_{p_id}")
                        edit_cat = st.selectbox(
                            "Category",
                            options=CATEGORIES,
                            index=CATEGORIES.index(p["category"]) if p["category"] in CATEGORIES else 0,
                            key=f"edt_cat_{p_id}"
                        )
                        if st.button("Save & Approve", key=f"save_apprv_{p_id}", type="primary", use_container_width=True):
                            update_proverb(
                                proverb_id=p_id,
                                proverb=edit_proverb,
                                english_translation=edit_trans,
                                meaning=edit_meaning,
                                cultural_context=edit_context,
                                category=edit_cat,
                                moderator="maintainer"
                            )
                            approve_proverb(p_id, moderator="maintainer", notes="Edited and approved by maintainer")
                            st.rerun()


# ==========================================
# TAB 2: Approved Corpus Management
# ==========================================
with tab_approved:
    if not approved_list:
        st.info("No approved proverbs found.")
    else:
        filter_apprv_lang = st.selectbox(
            "Filter by Language",
            options=["All"] + LANGUAGE_NAMES,
            key="mod_apprv_filter_lang"
        )
        filtered_approved = approved_list
        if filter_apprv_lang != "All":
            filtered_approved = [x for x in approved_list if x["language"] == filter_apprv_lang]

        st.caption(f"Displaying **{len(filtered_approved)}** approved records")

        for item in filtered_approved:
            i_id = item["id"]
            with st.expander(f"[{item['language']}] #{i_id}: {item['proverb'][:45]}..."):
                with st.container(border=True):
                    c_edit, c_del = st.columns([0.72, 0.28])

                    with c_edit:
                        with st.form(f"edit_approved_form_{i_id}"):
                            e_text = st.text_input("Proverb Text", value=item["proverb"])
                            e_trans = st.text_input("Translation", value=item.get("english_translation") or "")
                            e_mean = st.text_area("Meaning", value=item["meaning"])
                            e_ctx = st.text_area("Context", value=item.get("cultural_context") or "")
                            e_cat = st.selectbox(
                                "Category",
                                options=CATEGORIES,
                                index=CATEGORIES.index(item["category"]) if item["category"] in CATEGORIES else 0
                            )
                            if st.form_submit_button("Save Changes", type="primary"):
                                update_proverb(
                                    proverb_id=i_id,
                                    proverb=e_text,
                                    english_translation=e_trans,
                                    meaning=e_mean,
                                    cultural_context=e_ctx,
                                    category=e_cat,
                                    moderator="maintainer"
                                )
                                st.success("Updated successfully.")
                                st.rerun()

                    with c_del:
                        with st.container(border=True):
                            st.caption("Status Management")
                            if st.button("Move to Pending", key=f"unapprv_{i_id}", use_container_width=True):
                                restore_proverb_to_pending(i_id, moderator="maintainer", reason="Moved back for re-review")
                                st.rerun()

                            st.divider()
                            del_confirm = st.checkbox("Confirm deletion", key=f"del_chk_{i_id}")
                            if st.button("Delete Permanently", key=f"del_btn_{i_id}", disabled=not del_confirm, use_container_width=True):
                                delete_proverb(i_id, moderator="maintainer")
                                st.rerun()


# ==========================================
# TAB 3: Rejected Archive
# ==========================================
with tab_rejected:
    if not rejected_list:
        st.info("No rejected submissions on record.")
    else:
        for r in rejected_list:
            r_id = r["id"]
            with st.expander(f"[{r['language']}] #{r_id}: {r['proverb'][:45]}..."):
                with st.container(border=True):
                    st.markdown(f"**Proverb:** {r['proverb']}")
                    st.markdown(f"**Rejection Reason:** :red[{r.get('rejection_reason') or 'None specified'}]")
                    st.caption(f"Submitted on {format_iso_date(r['created_at'])}")

                    col_rest, col_del = st.columns(2)
                    with col_rest:
                        if st.button("Restore to Pending", key=f"rest_{r_id}", use_container_width=True):
                            restore_proverb_to_pending(r_id, moderator="maintainer", reason="Restored from archive")
                            st.rerun()

                    with col_del:
                        del_rej_chk = st.checkbox("Confirm permanent deletion", key=f"del_rej_chk_{r_id}")
                        if st.button("Delete", key=f"del_rej_{r_id}", disabled=not del_rej_chk, use_container_width=True):
                            delete_proverb(r_id, moderator="maintainer")
                            st.rerun()


# ==========================================
# TAB 4: Audit Trail
# ==========================================
with tab_logs:
    if not logs_list:
        st.info("No moderation audit logs recorded yet.")
    else:
        log_display = []
        for l in logs_list:
            log_display.append({
                "Log ID": l["id"],
                "Proverb ID": l["proverb_id"],
                "Action": l["action"].upper(),
                "Moderator": l.get("moderator") or "System",
                "Reason / Notes": l.get("reason") or "-",
                "Timestamp": format_iso_date(l["timestamp"], include_time=True)
            })
        st.dataframe(log_display, use_container_width=True, height=450)


# ==========================================
# TAB 5: Maintainer Export
# ==========================================
with tab_export:
    all_data = export_proverbs(approved_only=False, include_maintainer_meta=True)
    st.markdown(f"Complete dataset containing **{len(all_data)}** records across all moderation statuses (approved, pending, rejected).")

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        m_csv = generate_csv_export(all_data, is_maintainer=True)
        st.download_button(
            label="Download Complete CSV (with Audit Metadata)",
            data=m_csv,
            file_name=get_export_filename("bhashaverse_full", "csv"),
            mime="text/csv",
            type="primary",
            use_container_width=True
        )

    with col_m2:
        m_json = generate_json_export(all_data, is_maintainer=True)
        st.download_button(
            label="Download Complete JSON (with Audit Metadata)",
            data=m_json,
            file_name=get_export_filename("bhashaverse_full", "json"),
            mime="application/json",
            use_container_width=True
        )
