"""Agent Analytics dashboard rendering performance metrics, distributions, and error audits."""

import streamlit as st
from aidy.data.loader import load_cleaned_dataset
from aidy.analytics.visualizations import (
    plot_quality_by_agent_role_plotly,
    plot_duration_vs_quality_plotly,
    plot_token_and_error_plotly,
)
from aidy.ui.theme import page_header, section_title


def render_agent_analytics_page():
    page_header(
        "Agent analytics",
        "Performance across agent roles and research domains, from 500 recorded crew runs.",
        eyebrow="Insights",
    )

    df = load_cleaned_dataset("data/processed/dataset_cleaned.csv")

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        roles_available = ["All roles"] + sorted(df["agent_role"].unique().tolist())
        selected_role = st.selectbox("Agent role", options=roles_available)
    with col_f2:
        tasks_available = ["All topics"] + sorted(df["task_type"].unique().tolist())
        selected_task = st.selectbox("Topic", options=tasks_available)

    df_filtered = df.copy()
    if selected_role != "All roles":
        df_filtered = df_filtered[df_filtered["agent_role"] == selected_role]
    if selected_task != "All topics":
        df_filtered = df_filtered[df_filtered["task_type"] == selected_task]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Sample size", f"{len(df_filtered)} runs")
    m2.metric("Mean quality", f"{df_filtered['quality_score'].mean():.3f}")
    m3.metric("Mean duration", f"{df_filtered['duration_s'].mean():.1f}s")
    m4.metric("Error rate", f"{(df_filtered['errors'] > 0).mean() * 100:.1f}%")

    section_title("Quality by agent role")
    fig1 = plot_quality_by_agent_role_plotly(df if selected_role == "All roles" else df_filtered)
    st.plotly_chart(fig1, width="stretch")

    section_title("Duration vs. quality")
    fig2 = plot_duration_vs_quality_plotly(df_filtered)
    st.plotly_chart(fig2, width="stretch")

    section_title("Tokens & errors")
    fig3 = plot_token_and_error_plotly(df if selected_role == "All roles" else df_filtered)
    st.plotly_chart(fig3, width="stretch")
