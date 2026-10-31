"""Live Research Workspace displaying real-time agent execution timeline, sources, and claim audits."""

from html import escape

import streamlit as st
import pandas as pd
from aidy.crew.workflow import ResearchWorkflowRunner
from aidy.persistence.database import SessionLocal, init_db
from aidy.persistence.repositories import RunRepository
from aidy.export.markdown_export import format_report_as_markdown, save_markdown_report
from aidy.export.pdf_export import export_report_to_pdf
from aidy.ui.theme import page_header, card, pill, stamp, render_html

CLAIM_TONES = {"Verified": "success", "Contradicted": "error"}


def render_live_workspace_page():
    page_header("Live workspace", eyebrow="Run")

    query = st.session_state.get("active_query")
    latest_result = st.session_state.get("latest_run_result")

    # If user triggered a new inquiry, execute the workflow
    if query:
        render_html(f"<p>Researching <b style='color:var(--text)'>{escape(query.topic)}</b></p>")

        progress_bar = st.progress(0.0)
        status_box = st.empty()

        def status_callback(stage: str, msg: str, details: dict):
            idx = details.get("stage_idx", 1)
            pct = min(1.0, idx / 7.0)
            progress_bar.progress(pct)
            status_box.info(f"**Stage {idx}/7 · {stage.title()}** — {msg}")

        runner = ResearchWorkflowRunner()
        result = runner.run(query, status_callback=status_callback)

        # Clear progress indicators
        progress_bar.empty()
        status_box.empty()
        st.success(f"Completed in {result['duration_s']}s")

        # Format and persist report
        md_content = format_report_as_markdown(result["report"])
        save_markdown_report(result["report"])

        pdf_path = f"data/reports/{result['report'].report_id}.pdf"
        try:
            export_report_to_pdf(result["report"], pdf_path)
        except Exception as pe:
            st.warning(f"PDF export warning: {pe}")

        # Persist to database
        init_db()
        db = SessionLocal()
        try:
            repo = RunRepository(db)
            repo.save_run(
                run_id=result["run_id"],
                topic=query.topic,
                duration_s=result["duration_s"],
                tokens_used=result["tokens_used"],
                quality_score=result["quality_score"],
                errors=result["errors"],
                sources=result["sources"],
                claims=result["verified_claims"],
                report=result["report"],
                markdown_content=md_content,
                is_offline_demo=result["report"].is_offline_demo,
            )
        finally:
            db.close()

        # Cache result and clear active query to prevent re-execution loops
        st.session_state["latest_run_result"] = result
        st.session_state["selected_report_id"] = result["report"].report_id
        st.session_state["active_query"] = None
        latest_result = result

    if not latest_result:
        card(
            "<p>Nothing is running yet. Compose a question and the crew will start working here in real time.</p>",
            title="No active run",
        )
        if st.button("Go to New Research →", type="primary"):
            st.session_state["nav_request"] = "New Research"
            st.rerun()
        return

    r = latest_result
    rep = r["report"]

    mode = pill("Live · open-web retrieval", "success") if not rep.is_offline_demo else pill("Offline demo · verified benchmark", "warning")
    render_html(mode)
    st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)

    t1, t2, t3, t4 = st.columns(4)
    t1.metric("Run ID", r["run_id"])
    t2.metric("Latency", f"{r['duration_s']}s")
    t3.metric("Tokens", f"{r['tokens_used']:,}", help=f"Mode: {rep.token_accounting_mode}")
    t4.metric("Quality", f"{r['quality_score']:.2f}")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    tab_sources, tab_claims, tab_synthesis, tab_report = st.tabs([
        "Sources",
        "Claim audit",
        "Synthesis",
        "Report",
    ])

    with tab_sources:
        sources_data = []
        for s in r["sources"]:
            sources_data.append({
                "Citation": f"[{s.citation_id}]",
                "Title": s.title,
                "Domain": s.domain,
                "Published": s.published_date or "N/A",
                "Retrieval": getattr(s, "retrieval_mode", "OFFLINE_DEMO"),
                "Verified": "Yes" if s.is_verified else "Unverified",
                "Evidence": s.supporting_evidence_excerpt[:90] + "..." if s.supporting_evidence_excerpt else s.snippet[:90] + "...",
                "URL": s.url,
            })
        st.dataframe(
            pd.DataFrame(sources_data),
            width="stretch",
            hide_index=True,
            column_config={"URL": st.column_config.LinkColumn("URL")},
        )

    with tab_claims:
        for c in r["verified_claims"]:
            verdict = stamp(c.verification_status.upper(), CLAIM_TONES.get(c.verification_status, "warning"))
            citations_str = ", ".join(f"[{cid}]" for cid in c.supporting_citation_ids) or "None"
            quote_row = (
                f'<div class="stage"><span class="label">Evidence</span>'
                f'<div class="stage-value quote">“{escape(c.supporting_evidence_quote)}”</div></div>'
                if c.supporting_evidence_quote else ""
            )
            render_html(
                f"""
                <div class="slip">
                    <div class="slip-head"><span class="label">Claim {c.claim_id}</span>{verdict}</div>
                    <div class="stage"><span class="label">Statement</span><div class="stage-value serif">{escape(c.statement)}</div></div>
                    {quote_row}
                    <div class="stage"><span class="label">Rationale</span><div class="stage-value">{escape(c.rationale)}</div></div>
                    <div class="stage"><span class="label">Citations</span><div class="stage-value mono">{citations_str} · confidence {int(c.confidence * 100)}%</div></div>
                </div>
                """
            )

    with tab_synthesis:
        syn = r["synthesis"]
        sections = [
            ("Patterns & convergences", syn.key_patterns),
            ("Disagreements & tensions", syn.disagreements_and_tensions),
            ("Research gaps", syn.research_gaps),
        ]
        for col, (title, items) in zip(st.columns(3), sections):
            with col:
                card("<ul>" + "".join(f"<li>{escape(i)}</li>" for i in items) + "</ul>", title=title)

    with tab_report:
        render_html(f"<p>{pill(rep.review_status, 'warning')} &nbsp;<code>{rep.report_id}</code></p>")
        with st.container(key="sheet"):
            st.markdown(format_report_as_markdown(rep))
        if st.button("Open in Reports to edit & approve →", type="primary"):
            st.session_state["nav_request"] = "Reports"
            st.session_state["selected_report_id"] = rep.report_id
            st.rerun()
