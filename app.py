"""aidy.AI — Multi-Agent Research Assistant with CrewAI.

Main Streamlit Application Entry Point.
"""

import sys
import os

# Ensure src/ is on python path
sys.path.insert(0, os.path.abspath("src"))

import streamlit as st
from aidy.core.config import settings
from aidy.ui.theme import apply_theme, render_brand, render_bar_status
from aidy.persistence.database import init_db

# Page routes
from aidy.ui.pages.overview import render_overview_page
from aidy.ui.pages.new_research import render_new_research_page
from aidy.ui.pages.live_workspace import render_live_workspace_page
from aidy.ui.pages.reports_library import render_reports_library_page
from aidy.ui.pages.agent_analytics import render_agent_analytics_page
from aidy.ui.pages.dataset_explorer import render_dataset_explorer_page
from aidy.ui.pages.evaluation_center import render_evaluation_center_page
from aidy.ui.pages.settings import render_settings_page


PAGES = {
    "Overview": render_overview_page,
    "New Research": render_new_research_page,
    "Live Workspace": render_live_workspace_page,
    "Reports": render_reports_library_page,
    "Analytics": render_agent_analytics_page,
    "Datasets": render_dataset_explorer_page,
    "Evaluation": render_evaluation_center_page,
    "Settings": render_settings_page,
}


def main():
    st.set_page_config(
        page_title="aidy.AI",
        page_icon="✦",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Initialize database tables
    init_db()

    apply_theme()

    page_names = list(PAGES)

    # The nav radio owns its state under a fixed key, so its widget identity never changes
    # between reruns. Pages request navigation via "nav_request", applied here before the
    # widget is created (Streamlit forbids writing a widget's key after it renders).
    request = st.session_state.pop("nav_request", None)
    if request in PAGES:
        st.session_state["nav"] = request
    elif st.session_state.get("nav") not in PAGES:
        st.session_state["nav"] = "Overview"

    # Top bar: brand | navigation | status
    with st.container(key="topbar"):
        col_brand, col_nav, col_status = st.columns([1.15, 8, 1.3], vertical_alignment="center")
        with col_brand:
            render_brand()
        with col_nav:
            selection = st.radio(
                "Navigation",
                options=page_names,
                key="nav",
                horizontal=True,
                label_visibility="collapsed",
            )
        with col_status:
            mode = "Live search" if settings.has_live_search_credentials else "Offline demo"
            render_bar_status([("Mode", mode)])

    PAGES[selection]()


if __name__ == "__main__":
    main()
