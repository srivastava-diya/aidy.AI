"""Overview Dashboard page for aidy.AI."""

from html import escape

import streamlit as st
from aidy.persistence.database import SessionLocal, init_db
from aidy.persistence.repositories import RunRepository
from aidy.ui.theme import page_header, section_title, pillars, render_html


def render_overview_page():
    init_db()
    db = SessionLocal()
    repo = RunRepository(db)

    try:
        metrics = repo.get_live_metrics()
        recent_runs = repo.list_recent_runs(limit=10)
    finally:
        db.close()

    page_header(
        "Research,",
        "A crew of specialised agents researches, fact-checks, and writes. Every claim is grounded "
        "in a cited primary source; every report is reviewed by a human before it ships.",
        eyebrow="Multi-agent research desk",
        emphasis="verified.",
    )

    col_cta, _ = st.columns([1, 3])
    with col_cta:
        if st.button("Start new research →", type="primary"):
            st.session_state["nav_request"] = "New Research"
            st.rerun()

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4, gap="large")
    k1.metric("Total runs", metrics["total_runs"])
    k2.metric("Successful", metrics["successful_runs"])
    k3.metric("Avg quality", f"{metrics['avg_quality']:.2f}")
    k4.metric("Avg duration", f"{metrics['avg_duration_s']}s")

    section_title("How it works", "Four agents · one human")
    pillars([
        ("Autonomous sourcing", "Breaks your question into objectives, retrieves peer-reviewed and regulatory literature, and keeps a traceable excerpt for every source."),
        ("Adversarial fact-checking", "A dedicated agent audits every assertion against primary text. Anything unsupported is stamped, not slipped into the report."),
        ("Human sign-off", "Reports stay in draft until a specialist approves them, then export to Markdown or PDF with indexed citations."),
    ])

    section_title("Recent runs", f"{len(recent_runs)} shown")

    if not recent_runs:
        render_html('<div class="empty-note">No runs yet — start your first investigation from New Research.</div>')
        return

    rows = "".join(
        f"<tr><td>{escape(r.run_id)}</td>"
        f"<td class='topic'>{escape(r.topic)}</td>"
        f"<td>{r.created_at.strftime('%Y-%m-%d %H:%M') if r.created_at else 'N/A'}</td>"
        f"<td class='num'>{r.duration_s:.1f}s</td>"
        f"<td class='num'>{r.tokens_used:,}</td>"
        f"<td class='num'>{r.quality_score:.3f}</td>"
        f"<td class='num'>{r.errors}</td>"
        f"<td>{'OFFLINE' if r.is_offline_demo else 'LIVE'}</td></tr>"
        for r in recent_runs
    )
    render_html(
        f"""
        <div class="ledger-wrap"><table class="ledger">
            <thead><tr><th>Run</th><th>Topic</th><th>Created</th><th class="num">Duration</th>
            <th class="num">Tokens</th><th class="num">Quality</th><th class="num">Errors</th><th>Mode</th></tr></thead>
            <tbody>{rows}</tbody>
        </table></div>
        """
    )
