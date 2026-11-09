"""
BhashaVerse 2.0 - Maintainer Moderation Dashboard
Restricted-access management interface for community proverbs review,
verification, categorization, edit-before-approval, rejection logging,
and audit trail inspection.
"""

import streamlit as st

st.set_page_config(
    page_title="Moderation | BhashaVerse 2.0",
    page_icon="🛡️",
    layout="wide"
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
from components.footer import render_footer

render_header(title="🛡️ Moderation Console", badge_text="Restricted")
render_sidebar()

# ==========================================
# Authentication Gateway
# ==========================================
if not is_moderator_authenticated(st.session_state):
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("moderator_login_form"):
            st.markdown("#### Maintainer Access")
            passkey_input = st.text_input(
                "Passkey",
                type="password",
                placeholder="Enter maintainer key..."
            )
            submit_btn = st.form_submit_button("🔓 Unlock Console", type="primary", use_container_width=True)

            if submit_btn:
                if authenticate_moderator(st.session_state, passkey_input):
                    st.success("Authenticated.")
                    st.rerun()
                else:
                    st.error("Invalid key.")

    render_footer()
    st.stop()


# ==========================================
# Authenticated Maintainer Toolbar
# ==========================================
top_col1, top_col2 = st.columns([4, 1])
with top_col1:
    st.markdown("##### 🟢 Maintainer Mode Active")
with top_col2:
    if st.button("🚪 Log Out", use_container_width=True):
        logout_moderator(st.session_state)
        st.rerun()

st.divider()

# Fetch active counts
pending_list = get_pending_proverbs()
approved_list = get_approved_proverbs(limit=200)
rejected_list = get_rejected_proverbs()
logs_list = get_moderation_logs(limit=100)

tab_pending, tab_approved, tab_rejected, tab_logs, tab_export = st.tabs([
    f"Pending ({len(pending_list)})",
    f"Approved ({len(approved_list)})",
    f"Rejected ({len(rejected_list)})",
    f"Audit Logs ({len(logs_list)})",
    "Export All"
])

# ==========================================
# TAB 1: Pending Review
# ==========================================
with tab_pending:
    if not pending_list:
        st.info("Queue is empty.")
    else:
        for p in pending_list:
            p_id = p["id"]
            lang = p["language"]
            display_lang = get_display_label(lang)
            rtl = is_rtl(lang)
            rtl_style = "direction: rtl; text-align: right;" if rtl else "direction: ltr; text-align: left;"

            with st.expander(f"[{display_lang}] #{p_id}: {p['proverb'][:50]}...", expanded=True):
                info_col1, info_col2 = st.columns([2, 1])

                with info_col1:
                    st.markdown(
                        f"""
                        <div style="background: var(--bv-surface); padding: 0.85rem; border-radius: 6px; border: 1px solid var(--bv-border); margin-bottom: 0.75rem;">
                            <div style="font-size: 1.2rem; font-weight: 600; color: var(--bv-text); {rtl_style} margin-bottom: 0.4rem;">
                                {sanitize_text(p['proverb'])}
                            </div>
                            <div style="color: var(--bv-muted); font-size: 0.9rem; margin-bottom: 0.3rem;">
                                <strong>Translation:</strong> {sanitize_text(p.get('english_translation') or '-')}
                            </div>
                            <div style="color: var(--bv-text); font-size: 0.9rem; margin-bottom: 0.3rem;">
                                <strong>Meaning:</strong> {sanitize_text(p['meaning'])}
                            </div>
                            <div style="color: var(--bv-muted); font-size: 0.85rem;">
                                <strong>Context:</strong> {sanitize_text(p.get('cultural_context') or '-')}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with info_col2:
                    st.markdown(
                        f"""
                        <div style="background: var(--bv-surface); padding: 0.75rem; border-radius: 6px; font-size: 0.82rem; border: 1px solid var(--bv-border); color: var(--bv-text);">
                            <div><strong>UUID:</strong> <code>{p['submission_uuid'][:8]}</code></div>
                            <div><strong>Category:</strong> {p['category']}</div>
                            <div><strong>Submitted:</strong> {format_iso_date(p['created_at'])}</div>
                            <div><strong>Contributor:</strong> {sanitize_text(p.get('contributor_name') or 'Anonymous')}</div>
                            <div><strong>Email:</strong> {sanitize_text(p.get('contributor_email') or '-')}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # Action Buttons
                action_col1, action_col2, action_col3 = st.columns([1, 1, 1.2])

                with action_col1:
                    if st.button(f"✅ Approve", key=f"apprv_{p_id}", type="primary", use_container_width=True):
                        if approve_proverb(p_id, moderator="maintainer"):
                            st.success(f"Approved #{p_id}")
                            st.rerun()

                with action_col2:
                    with st.popover("❌ Reject", use_container_width=True):
                        reject_reason = st.text_input("Reason", placeholder="Reason...", key=f"rej_reason_{p_id}")
                        if st.button("Confirm Reject", key=f"conf_rej_{p_id}", type="primary"):
                            if reject_proverb(p_id, reason=reject_reason, moderator="maintainer"):
                                st.rerun()

                with action_col3:
                    with st.popover("✏️ Edit & Approve", use_container_width=True):
                        edit_proverb = st.text_input("Proverb", value=p["proverb"], key=f"edt_prv_{p_id}")
                        edit_trans = st.text_input("Translation", value=p.get("english_translation") or "", key=f"edt_tr_{p_id}")
                        edit_meaning = st.text_area("Meaning", value=p["meaning"], key=f"edt_mn_{p_id}")
                        edit_context = st.text_area("Context", value=p.get("cultural_context") or "", key=f"edt_ctx_{p_id}")
                        edit_cat = st.selectbox(
                            "Category",
                            options=CATEGORIES,
                            index=CATEGORIES.index(p["category"]) if p["category"] in CATEGORIES else 0,
                            key=f"edt_cat_{p_id}"
                        )
                        if st.button("Save & Approve", key=f"save_apprv_{p_id}", type="primary"):
                            update_proverb(
                                proverb_id=p_id,
                                proverb=edit_proverb,
                                english_translation=edit_trans,
                                meaning=edit_meaning,
                                cultural_context=edit_context,
                                category=edit_cat,
                                moderator="maintainer"
                            )
                            approve_proverb(p_id, moderator="maintainer", notes="Edited and approved")
                            st.rerun()


# ==========================================
# TAB 2: Approved Corpus Management
# ==========================================
with tab_approved:
    if not approved_list:
        st.info("No approved proverbs.")
    else:
        filter_apprv_lang = st.selectbox(
            "Filter Language",
            options=["All"] + LANGUAGE_NAMES,
            key="mod_apprv_filter_lang"
        )
        filtered_approved = approved_list
        if filter_apprv_lang != "All":
            filtered_approved = [x for x in approved_list if x["language"] == filter_apprv_lang]

        for item in filtered_approved:
            i_id = item["id"]
            with st.expander(f"[{item['language']}] #{i_id}: {item['proverb'][:40]}..."):
                c_edit, c_del = st.columns([3, 1])

                with c_edit:
                    with st.form(f"edit_approved_form_{i_id}"):
                        e_text = st.text_input("Proverb", value=item["proverb"])
                        e_trans = st.text_input("Translation", value=item.get("english_translation") or "")
                        e_mean = st.text_area("Meaning", value=item["meaning"])
                        e_ctx = st.text_area("Context", value=item.get("cultural_context") or "")
                        e_cat = st.selectbox(
                            "Category",
                            options=CATEGORIES,
                            index=CATEGORIES.index(item["category"]) if item["category"] in CATEGORIES else 0
                        )
                        if st.form_submit_button("Save Changes"):
                            update_proverb(
                                proverb_id=i_id,
                                proverb=e_text,
                                english_translation=e_trans,
                                meaning=e_mean,
                                cultural_context=e_ctx,
                                category=e_cat,
                                moderator="maintainer"
                            )
                            st.success("Saved.")
                            st.rerun()

                with c_del:
                    if st.button("Move to Pending", key=f"unapprv_{i_id}"):
                        restore_proverb_to_pending(i_id, moderator="maintainer", reason="Moved back")
                        st.rerun()

                    st.markdown("---")
                    del_confirm = st.checkbox("Confirm delete", key=f"del_chk_{i_id}")
                    if st.button("🗑️ Delete", key=f"del_btn_{i_id}", disabled=not del_confirm):
                        delete_proverb(i_id, moderator="maintainer")
                        st.rerun()


# ==========================================
# TAB 3: Rejected Archive
# ==========================================
with tab_rejected:
    if not rejected_list:
        st.info("No rejected submissions.")
    else:
        for r in rejected_list:
            r_id = r["id"]
            with st.expander(f"[{r['language']}] #{r_id}: {r['proverb'][:40]}..."):
                st.markdown(f"**Proverb:** {r['proverb']}")
                st.markdown(f"**Reason:** *{r.get('rejection_reason') or '-'}*")

                col_rest, col_del = st.columns([1, 1])
                with col_rest:
                    if st.button(f"🔄 Restore to Pending", key=f"rest_{r_id}", use_container_width=True):
                        restore_proverb_to_pending(r_id, moderator="maintainer", reason="Restored")
                        st.rerun()

                with col_del:
                    del_rej_chk = st.checkbox("Confirm", key=f"del_rej_chk_{r_id}")
                    if st.button(f"🗑️ Delete", key=f"del_rej_{r_id}", disabled=not del_rej_chk, use_container_width=True):
                        delete_proverb(r_id, moderator="maintainer")
                        st.rerun()


# ==========================================
# TAB 4: Audit Trail
# ==========================================
with tab_logs:
    if not logs_list:
        st.info("No audit logs.")
    else:
        log_display = []
        for l in logs_list:
            log_display.append({
                "ID": l["id"],
                "Proverb ID": l["proverb_id"],
                "Action": l["action"].upper(),
                "Actor": l.get("moderator") or "System",
                "Reason": l.get("reason") or "-",
                "Timestamp": format_iso_date(l["timestamp"], include_time=True)
            })
        st.dataframe(log_display, use_container_width=True, height=400)


# ==========================================
# TAB 5: Maintainer Export
# ==========================================
with tab_export:
    all_data = export_proverbs(approved_only=False, include_maintainer_meta=True)
    st.markdown(f"Total Records: **{len(all_data)}**")

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        m_csv = generate_csv_export(all_data, is_maintainer=True)
        st.download_button(
            label="📥 Full CSV",
            data=m_csv,
            file_name=get_export_filename("bhashaverse_full", "csv"),
            mime="text/csv",
            type="primary",
            use_container_width=True
        )

    with col_m2:
        m_json = generate_json_export(all_data, is_maintainer=True)
        st.download_button(
            label="📦 Full JSON",
            data=m_json,
            file_name=get_export_filename("bhashaverse_full", "json"),
            mime="application/json",
            use_container_width=True
        )

render_footer()
