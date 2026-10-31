"""New Research page for parameter configuration and dispatch."""

import streamlit as st
from aidy.core.config import settings
from aidy.crew.schemas import ResearchQuery
from aidy.ui.theme import page_header, pill, box_head, render_html


def render_new_research_page():
    page_header(
        "New research",
        "Define the question and scope. The crew handles retrieval, verification, synthesis, and writing.",
        eyebrow="Compose",
    )

    if settings.has_live_search_credentials and settings.has_live_llm_credentials:
        render_html(pill("◆ Live mode — external search and LLM providers configured", "success"))
    else:
        render_html(pill("◆ Demo mode — curated benchmark sources with strict citation grounding", "warning"))
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    with st.form("research_form", border=False):
        with st.container(key="fbox_question"):
            box_head("01", "✦", "The question", "What should the crew investigate?")
            topic = st.text_input(
                "✦ Research question",
                value="Research the current applications, benefits, limitations, and future scope of Agentic AI in healthcare.",
                help="Enter a focused, technical or academic research question.",
            )

            subquestions_raw = st.text_area(
                "↳ Sub-questions — optional, one per line",
                value="",
                placeholder=(
                    "Leave blank to derive objectives from the topic automatically.\n"
                    "e.g. What clinical applications show the highest measured accuracy?"
                ),
                help="Granular inquiries for the Researcher agent. If omitted, aidy.AI derives research dimensions from your topic.",
                height=100,
            )

        with st.container(key="fbox_scope"):
            box_head("02", "◎", "Scope", "How wide and how deep?")
            col1, col2 = st.columns(2, gap="large")
            with col1:
                depth = st.selectbox(
                    "◐ Depth",
                    options=["standard", "comprehensive", "deep_dive"],
                    index=1,
                    format_func=lambda d: d.replace("_", " ").title(),
                    help="Controls retrieval breadth and analysis granularity.",
                )
            with col2:
                max_sources = st.slider(
                    "№ Maximum sources",
                    min_value=2,
                    max_value=10,
                    value=5,
                    help="Maximum unique publications to retrieve and cross-examine.",
                )

            constraints = st.text_input(
                "⊘ Boundaries — optional",
                value="Focus on peer-reviewed clinical literature and published regulatory guidelines from 2023-2026.",
                help="Specify domain constraints or excluded topics.",
            )

        submitted = st.form_submit_button("Launch crew →", width="stretch")

    if submitted:
        if not topic.strip():
            st.error("Research topic cannot be empty.")
            return

        subquestions = [q.strip() for q in subquestions_raw.splitlines() if q.strip()]

        query = ResearchQuery(
            topic=topic.strip(),
            subquestions=subquestions,
            depth=depth,
            max_sources=max_sources,
            constraints=constraints.strip() if constraints else None,
        )

        # Store in session state for live workspace execution
        st.session_state["active_query"] = query
        st.session_state["nav_request"] = "Live Workspace"
        st.rerun()
