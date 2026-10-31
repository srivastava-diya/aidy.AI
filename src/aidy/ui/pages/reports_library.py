"""Reports Library page for exploring, editing, approving, and exporting reports."""

import os
import streamlit as st
from aidy.persistence.database import SessionLocal, init_db
from aidy.persistence.repositories import ReportRepository
from aidy.ui.theme import page_header, card, pill, render_html

STATUS_TONES = {"draft": "warning", "reviewed": "accent", "final": "success"}


def render_reports_library_page():
    init_db()
    db = SessionLocal()
    repo = ReportRepository(db)

    try:
        reports = repo.list_reports(limit=50)
    finally:
        db.close()

    page_header("Reports", "Review, edit, approve, and export research reports.", eyebrow="Library")

    if not reports:
        card("<p>Run an investigation from <b>New Research</b> to populate the library.</p>", title="No reports yet")
        return

    report_options = {f"{r.report_id} — {r.topic} [{r.review_status.upper()}]": r.report_id for r in reports}

    # Check if a specific report was pre-selected
    preselected = st.session_state.get("selected_report_id")
    default_idx = 0
    if preselected:
        for idx, rep_id in enumerate(report_options.values()):
            if rep_id == preselected:
                default_idx = idx
                break

    selected_label = st.selectbox("Report", options=list(report_options.keys()), index=default_idx)
    selected_id = report_options[selected_label]

    # Fetch active report
    db = SessionLocal()
    try:
        report = repo.get_report(selected_id)
        if not report:
            st.error("Report not found.")
            return

        render_html(
            f"<p>{pill(report.review_status.upper(), STATUS_TONES.get(report.review_status, 'neutral'))} "
            f"&nbsp;<code>{report.report_id}</code> &nbsp;·&nbsp; {report.created_at.strftime('%Y-%m-%d %H:%M')}</p>"
        )

        col_status, col_save, col_md, col_pdf = st.columns([1.4, 1, 1, 1], vertical_alignment="bottom")
        with col_status:
            new_status = st.selectbox(
                "Approval status",
                options=["draft", "reviewed", "final"],
                index=["draft", "reviewed", "final"].index(report.review_status),
                format_func=str.title,
                key=f"status_{report.report_id}",
            )
        with col_save:
            if st.button("Update status", type="primary", width="stretch"):
                repo.update_status(report.report_id, new_status)
                st.success(f"Status updated to '{new_status}'.")
                st.rerun()
        with col_md:
            st.download_button(
                label="Markdown",
                data=report.markdown_content,
                file_name=f"{report.report_id}.md",
                mime="text/markdown",
                width="stretch",
            )
        with col_pdf:
            pdf_path = f"data/reports/{report.report_id}.pdf"
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                st.download_button(
                    label="PDF",
                    data=pdf_bytes,
                    file_name=f"{report.report_id}.pdf",
                    mime="application/pdf",
                    width="stretch",
                )
            else:
                st.button("PDF unavailable", disabled=True, width="stretch")

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        tab_view, tab_edit = st.tabs(["Preview", "Edit"])

        with tab_view:
            with st.container(key="sheet"):
                st.markdown(report.markdown_content)

        with tab_edit:
            edited_text = st.text_area(
                "Markdown",
                value=report.markdown_content,
                height=500,
                key=f"editor_{report.report_id}",
            )
            if st.button("Save changes", type="primary"):
                repo.update_markdown(report.report_id, edited_text)
                disk_path = f"data/reports/{report.report_id}.md"
                if os.path.exists("data/reports"):
                    with open(disk_path, "w", encoding="utf-8") as f:
                        f.write(edited_text)
                st.success("Report saved (database and disk synchronized).")
                st.rerun()

    finally:
        db.close()
