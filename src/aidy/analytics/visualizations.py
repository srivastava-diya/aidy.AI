"""Visualization generation module for aidy.AI.

Provides:
1. High-resolution static matplotlib figures styled in the aidy.AI palette for reports and synopsis.
2. Interactive Plotly figures for the Streamlit dashboard and dataset explorer.
"""

import os
from typing import Optional
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import plotly.express as px
import plotly.graph_objects as go


# aidy.AI paper & ink palette (matches src/aidy/ui/theme.py)
PALETTE = {
    "bg": "#FBF9F4",
    "card": "#FBF9F4",
    "surface": "#F0ECE3",
    "accent": "#17140F",
    "accent_2": "#2C6144",
    "text_primary": "#17140F",
    "text_secondary": "#5A5349",
    "border": "#D7D0C1",
    "error": "#A02B1E",
}


def apply_plotly_layout(fig: go.Figure) -> go.Figure:
    """Flat paper & ink Plotly layout: mono ticks, dotted-feel hairline grid."""
    fig.update_layout(
        template="plotly_white",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="JetBrains Mono, monospace", color=PALETTE["text_secondary"], size=11),
        title=dict(text=None),
        margin=dict(l=10, r=10, t=20, b=10),
        hoverlabel=dict(bgcolor=PALETTE["bg"], bordercolor=PALETTE["accent"], font_color=PALETTE["text_primary"], font_family="JetBrains Mono, monospace"),
        legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    fig.update_xaxes(gridcolor="#E4DDCF", zeroline=False, linecolor=PALETTE["accent"], showline=True)
    fig.update_yaxes(gridcolor="#E4DDCF", zeroline=False, linecolor=PALETTE["border"])
    return fig


def apply_matplotlib_theme():
    """Configures matplotlib rcParams for the aidy.AI aesthetic."""
    plt.style.use("default")
    mpl.rcParams["figure.facecolor"] = PALETTE["bg"]
    mpl.rcParams["axes.facecolor"] = PALETTE["card"]
    mpl.rcParams["savefig.facecolor"] = PALETTE["bg"]
    mpl.rcParams["text.color"] = PALETTE["text_primary"]
    mpl.rcParams["axes.labelcolor"] = PALETTE["text_secondary"]
    mpl.rcParams["xtick.color"] = PALETTE["text_secondary"]
    mpl.rcParams["ytick.color"] = PALETTE["text_secondary"]
    mpl.rcParams["grid.color"] = PALETTE["border"]
    mpl.rcParams["grid.alpha"] = 0.6
    mpl.rcParams["font.sans-serif"] = ["Segoe UI", "DejaVu Sans", "Helvetica", "Arial"]
    mpl.rcParams["font.family"] = "sans-serif"


# --- Plot 1: Average Quality Score by Agent Role ---
def plot_quality_by_agent_role_static(df: pd.DataFrame, save_path: str = "docs/diagrams/eda_plot1_quality_by_role.png") -> str:
    """Generates Plot 1: Average quality score by agent role with confidence error bars."""
    apply_matplotlib_theme()
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=300)

    role_stats = df.groupby("agent_role")["quality_score"].agg(["mean", "std", "count"]).reset_index()
    role_stats = role_stats.sort_values(by="mean", ascending=False)

    bars = ax.bar(
        role_stats["agent_role"],
        role_stats["mean"],
        yerr=role_stats["std"] / np.sqrt(role_stats["count"]),
        capsize=5,
        color=PALETTE["accent"],
        edgecolor=PALETTE["border"],
        alpha=0.9,
    )

    ax.set_ylim(0.5, 1.05)
    ax.set_title("Average Quality Score by Agent Role (Mean +/- SEM)", fontsize=13, pad=12, color=PALETTE["text_primary"], weight="bold")
    ax.set_xlabel("Agent Role", fontsize=11, labelpad=8)
    ax.set_ylabel("Quality Score [0.0 - 1.0]", fontsize=11, labelpad=8)
    ax.grid(axis="y", linestyle="--")

    # Value labels
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:.3f}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
            color=PALETTE["text_primary"],
            weight="bold",
        )

    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig.savefig(save_path)
    plt.close(fig)
    return save_path


def plot_quality_by_agent_role_plotly(df: pd.DataFrame) -> go.Figure:
    """Interactive Plotly version of quality score by role."""
    role_stats = df.groupby("agent_role")["quality_score"].agg(["mean", "std", "count"]).reset_index()
    role_stats = role_stats.sort_values(by="mean", ascending=False)

    fig = px.bar(
        role_stats,
        x="agent_role",
        y="mean",
        error_y=role_stats["std"] / np.sqrt(role_stats["count"]),
        title="Average Quality Score by Agent Role (Mean +/- SEM)",
        labels={"agent_role": "Agent Role", "mean": "Average Quality Score"},
        color_discrete_sequence=[PALETTE["accent"]],
    )
    fig.update_traces(marker_line_width=0, marker_cornerradius=0)
    fig.update_layout(yaxis=dict(range=[0.5, 1.02]))
    return apply_plotly_layout(fig)


# --- Plot 2: Execution Duration vs Quality Score ---
def plot_duration_vs_quality_static(df: pd.DataFrame, save_path: str = "docs/diagrams/eda_plot2_duration_vs_quality.png") -> str:
    """Generates Plot 2: Scatter plot of duration versus quality score with trendline and error highlight."""
    apply_matplotlib_theme()
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=300)

    clean_mask = df["errors"] == 0
    error_mask = df["errors"] > 0

    ax.scatter(
        df.loc[clean_mask, "duration_s"],
        df.loc[clean_mask, "quality_score"],
        color=PALETTE["accent_2"],
        alpha=0.65,
        s=45,
        label="Clean Run (0 Errors)",
        edgecolors="none",
    )
    ax.scatter(
        df.loc[error_mask, "duration_s"],
        df.loc[error_mask, "quality_score"],
        color=PALETTE["error"],
        alpha=0.85,
        s=60,
        marker="^",
        label="Runs with Errors (1-2)",
        edgecolors="none",
    )

    # Linear trendline
    z = np.polyfit(df["duration_s"], df["quality_score"], 1)
    p = np.poly1d(z)
    x_vals = np.linspace(df["duration_s"].min(), df["duration_s"].max(), 100)
    ax.plot(x_vals, p(x_vals), color=PALETTE["accent"], linestyle="--", linewidth=1.8, label=f"Trendline (slope: {z[0]:.4f})")

    ax.set_title("Execution Duration vs. Quality Score", fontsize=13, pad=12, color=PALETTE["text_primary"], weight="bold")
    ax.set_xlabel("Execution Duration (seconds)", fontsize=11, labelpad=8)
    ax.set_ylabel("Quality Score [0.0 - 1.0]", fontsize=11, labelpad=8)
    ax.grid(True, linestyle="--")
    ax.legend(facecolor=PALETTE["surface"], edgecolor=PALETTE["border"], loc="lower right", fontsize=9)

    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig.savefig(save_path)
    plt.close(fig)
    return save_path


def plot_duration_vs_quality_plotly(df: pd.DataFrame) -> go.Figure:
    """Interactive Plotly version of duration vs quality score."""
    df_plot = df.copy()
    df_plot["Status"] = df_plot["errors"].apply(lambda e: "Run with Errors" if e > 0 else "Clean Run")

    fig = px.scatter(
        df_plot,
        x="duration_s",
        y="quality_score",
        color="Status",
        color_discrete_map={"Clean Run": PALETTE["accent_2"], "Run with Errors": PALETTE["error"]},
        hover_data=["run_id", "agent_role", "task_type", "tokens_used"],
        trendline="ols",
        title="Execution Duration vs. Quality Score",
        labels={"duration_s": "Execution Duration (s)", "quality_score": "Quality Score"},
    )
    fig.update_traces(marker=dict(size=7, opacity=0.75, line=dict(width=0)), selector=dict(mode="markers"))
    return apply_plotly_layout(fig)


# --- Plot 3: Token Consumption & Error Distribution ---
def plot_token_and_error_static(df: pd.DataFrame, save_path: str = "docs/diagrams/eda_plot3_tokens_and_errors.png") -> str:
    """Generates Plot 3: Dual-axis plot of token consumption and error rate by agent role."""
    apply_matplotlib_theme()
    fig, ax1 = plt.subplots(figsize=(8.5, 4.8), dpi=300)

    role_agg = (
        df.groupby("agent_role")
        .agg(avg_tokens=("tokens_used", "mean"), error_rate=("errors", lambda x: (x > 0).mean() * 100))
        .reset_index()
    )

    x = np.arange(len(role_agg))
    width = 0.38

    rects1 = ax1.bar(
        x - width / 2,
        role_agg["avg_tokens"],
        width,
        label="Avg Tokens Used",
        color=PALETTE["accent_2"],
        edgecolor=PALETTE["border"],
    )
    ax1.set_ylabel("Average Tokens Used", color=PALETTE["accent_2"], fontsize=11, labelpad=8)
    ax1.set_xticks(x)
    ax1.set_xticklabels(role_agg["agent_role"], fontsize=10)
    ax1.grid(axis="y", linestyle="--")

    ax2 = ax1.twinx()
    rects2 = ax2.bar(
        x + width / 2,
        role_agg["error_rate"],
        width,
        label="Error Rate (%)",
        color=PALETTE["error"],
        edgecolor=PALETTE["border"],
    )
    ax2.set_ylabel("Error Occurrence Rate (%)", color=PALETTE["error"], fontsize=11, labelpad=8)
    ax2.grid(False)

    plt.title("Token Consumption and Error Distribution by Agent Role", fontsize=13, pad=12, color=PALETTE["text_primary"], weight="bold")
    fig.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig.savefig(save_path)
    plt.close(fig)
    return save_path


def plot_token_and_error_plotly(df: pd.DataFrame) -> go.Figure:
    """Interactive Plotly version of tokens and errors by agent role."""
    role_agg = (
        df.groupby("agent_role")
        .agg(avg_tokens=("tokens_used", "mean"), error_rate=("errors", lambda x: (x > 0).mean() * 100))
        .reset_index()
    )

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=role_agg["agent_role"],
            y=role_agg["avg_tokens"],
            name="Avg Tokens Used",
            marker_color=PALETTE["accent_2"],
            yaxis="y1",
        )
    )
    fig.add_trace(
        go.Bar(
            x=role_agg["agent_role"],
            y=role_agg["error_rate"],
            name="Error Rate (%)",
            marker_color=PALETTE["error"],
            yaxis="y2",
        )
    )

    apply_plotly_layout(fig)
    fig.update_traces(marker_line_width=0, marker_cornerradius=0)
    fig.update_layout(
        barmode="group",
        yaxis=dict(title="Avg Tokens Used"),
        yaxis2=dict(
            title="Error Occurrence Rate (%)",
            overlaying="y",
            side="right",
            showgrid=False,
        ),
    )
    return fig


# --- Plot 4: Correlation Heatmap ---
def plot_correlation_heatmap_static(df: pd.DataFrame, save_path: str = "docs/diagrams/eda_plot4_correlation_heatmap.png") -> str:
    """Generates Plot 4: Correlation matrix among numerical variables."""
    apply_matplotlib_theme()
    fig, ax = plt.subplots(figsize=(6.5, 5), dpi=300)

    numeric_cols = ["tokens_used", "duration_s", "quality_score", "errors"]
    corr = df[numeric_cols].corr()

    cax = ax.matshow(corr, cmap="Greys", vmin=-0.3, vmax=1.0)
    fig.colorbar(cax, shrink=0.8, pad=0.04)

    for i in range(len(numeric_cols)):
        for j in range(len(numeric_cols)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", color=PALETTE["bg"] if abs(corr.iloc[i, j]) > 0.4 else PALETTE["text_primary"], weight="bold", fontsize=10)

    ax.set_xticks(range(len(numeric_cols)))
    ax.set_yticks(range(len(numeric_cols)))
    ax.set_xticklabels(numeric_cols, rotation=35, ha="left", fontsize=9)
    ax.set_yticklabels(numeric_cols, fontsize=9)
    ax.set_title("Operational Metrics Correlation Heatmap", fontsize=12, pad=18, weight="bold")

    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig.savefig(save_path)
    plt.close(fig)
    return save_path


def generate_all_eda_visualizations(df: pd.DataFrame, output_dir: str = "docs/diagrams"):
    """Generates and saves all publication-grade static figures."""
    os.makedirs(output_dir, exist_ok=True)
    p1 = plot_quality_by_agent_role_static(df, os.path.join(output_dir, "eda_plot1_quality_by_role.png"))
    p2 = plot_duration_vs_quality_static(df, os.path.join(output_dir, "eda_plot2_duration_vs_quality.png"))
    p3 = plot_token_and_error_static(df, os.path.join(output_dir, "eda_plot3_tokens_and_errors.png"))
    p4 = plot_correlation_heatmap_static(df, os.path.join(output_dir, "eda_plot4_correlation_heatmap.png"))
    print(f"Generated EDA plots: {p1}, {p2}, {p3}, {p4}")
    return [p1, p2, p3, p4]
