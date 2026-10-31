"""Script to generate publication-grade system architecture and data flow diagrams."""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from aidy.analytics.visualizations import apply_matplotlib_theme, PALETTE


def generate_architecture_block_diagram(save_path: str = "docs/diagrams/system_architecture.png"):
    """Generates the System Block Diagram."""
    apply_matplotlib_theme()
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    def draw_box(x, y, w, h, title, subtitle, color=PALETTE["card"], border_color=PALETTE["accent"]):
        rect = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=1.5",
            facecolor=color,
            edgecolor=border_color,
            linewidth=1.5,
        )
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h * 0.65, title, ha="center", va="center", color=PALETTE["text_primary"], weight="bold", fontsize=10)
        ax.text(x + w / 2, y + h * 0.35, subtitle, ha="center", va="center", color=PALETTE["text_secondary"], fontsize=7.5)

    def draw_arrow(x1, y1, x2, y2, label=""):
        ax.annotate(
            label,
            xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(facecolor=PALETTE["accent_2"], edgecolor=PALETTE["accent_2"], arrowstyle="->", lw=1.5),
            ha="center", va="center", color=PALETTE["text_secondary"], fontsize=7.5,
        )

    # Title
    ax.text(50, 95, "aidy.AI Multi-Agent Research System Architecture", ha="center", va="center", color=PALETTE["text_primary"], weight="bold", fontsize=14)

    # Layer 1: Presentation Layer
    draw_box(5, 74, 90, 14, "Presentation & Interaction Layer (Streamlit)", "Overview | New Research | Live Workspace | Reports Library | Analytics | Dataset Explorer", color=PALETTE["surface"], border_color=PALETTE["accent"])

    # Layer 2: Core Orchestration Layer
    draw_box(5, 46, 90, 22, "Multi-Agent Orchestration Engine (CrewAI & Workflow Runner)", "Coordinated Execution & Fact-Checking Protocols", color=PALETTE["bg"], border_color=PALETTE["accent_2"])

    # Agents inside orchestration
    draw_box(8, 49, 18, 14, "Researcher", "Search & Retrieval", color=PALETTE["card"])
    draw_box(29, 49, 18, 14, "Fact-Checker", "Evidence Audit", color=PALETTE["card"])
    draw_box(50, 49, 18, 14, "Analyst", "Synthesis & Gaps", color=PALETTE["card"])
    draw_box(71, 49, 18, 14, "Writer", "Report Authoring", color=PALETTE["card"])

    # Agent data arrows
    draw_arrow(26, 56, 29, 56)
    draw_arrow(47, 56, 50, 56)
    draw_arrow(68, 56, 71, 56)

    # Layer 3: Tools & External Gateways
    draw_box(5, 22, 42, 18, "External Tools & Safe Web Retrieval", "SerpAPI / Tavily | Safe Web Reader | SSRF Firewall", color=PALETTE["card"])
    draw_box(53, 22, 42, 18, "Persistence & Verification Layer", "SQLite / SQLAlchemy ORM | Source Registry | Reports", color=PALETTE["card"])

    # Layer 4: Foundation Models & Data
    draw_box(5, 3, 42, 14, "Foundation LLM Providers", "OpenAI GPT-4o / Gemini / Anthropic API", color=PALETTE["surface"])
    draw_box(53, 3, 42, 14, "Empirical Evaluation Dataset", "dataset.csv (500 rows) | synthetic_dataset (5,000)", color=PALETTE["surface"])

    # Connections between layers
    draw_arrow(50, 74, 50, 68, "User Task Dispatch")
    draw_arrow(17, 46, 17, 40)
    draw_arrow(74, 46, 74, 40)
    draw_arrow(26, 22, 26, 17)
    draw_arrow(74, 22, 74, 17)

    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig.savefig(save_path)
    plt.close(fig)
    print(f"Generated System Architecture Diagram: {save_path}")


def generate_dfd_level_0(save_path: str = "docs/diagrams/data_flow_diagram_level_0.png"):
    """Generates Data Flow Diagram Level 0."""
    apply_matplotlib_theme()
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    def draw_entity(x, y, w, h, text):
        rect = patches.Rectangle((x, y), w, h, facecolor=PALETTE["surface"], edgecolor=PALETTE["accent"], lw=1.5)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, text, ha="center", va="center", color=PALETTE["text_primary"], weight="bold", fontsize=9)

    def draw_process(x, y, r, text, num="0"):
        circle = patches.Circle((x, y), r, facecolor=PALETTE["card"], edgecolor=PALETTE["accent_2"], lw=1.5)
        ax.add_patch(circle)
        ax.text(x, y + 2, f"P{num}", ha="center", va="center", color=PALETTE["accent"], weight="bold", fontsize=8)
        ax.text(x, y - 3, text, ha="center", va="center", color=PALETTE["text_primary"], weight="bold", fontsize=8.5)

    def draw_datastore(x, y, w, h, text):
        # Open ended rectangle (two parallel horizontal lines)
        ax.plot([x, x + w], [y, y], color=PALETTE["accent_2"], lw=1.5)
        ax.plot([x, x + w], [y + h, y + h], color=PALETTE["accent_2"], lw=1.5)
        ax.plot([x, x], [y, y + h], color=PALETTE["accent_2"], lw=1.5)
        rect = patches.Rectangle((x, y), w, h, facecolor=PALETTE["card"], edgecolor="none")
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, text, ha="center", va="center", color=PALETTE["text_primary"], fontsize=8)

    ax.text(50, 93, "Data Flow Diagram (DFD Level 0) — aidy.AI", ha="center", va="center", color=PALETTE["text_primary"], weight="bold", fontsize=13)

    # Entities
    draw_entity(5, 55, 18, 16, "User / Specialist\n(Researcher)")
    draw_entity(77, 55, 18, 16, "External Web\n& Knowledge Sources")

    # Core Process
    draw_process(50, 63, 13, "aidy.AI\nMulti-Agent\nPlatform", "0")

    # Data Stores
    draw_datastore(35, 15, 30, 14, "D1: SQLite Database\n(Runs, Sources, Claims, Reports)")

    # Data flows
    # User -> Process
    ax.annotate("Research Query & Constraints", xy=(37, 66), xytext=(23, 66),
                arrowprops=dict(facecolor=PALETTE["accent"], edgecolor=PALETTE["accent"], arrowstyle="->", lw=1.2),
                ha="center", va="bottom", color=PALETTE["text_secondary"], fontsize=7.5)

    # Process -> User
    ax.annotate("Draft / Final Report & Sources", xy=(23, 60), xytext=(37, 60),
                arrowprops=dict(facecolor=PALETTE["accent_2"], edgecolor=PALETTE["accent_2"], arrowstyle="->", lw=1.2),
                ha="center", va="top", color=PALETTE["text_secondary"], fontsize=7.5)

    # Process -> Web
    ax.annotate("Search Query & HTTP Fetch", xy=(77, 66), xytext=(63, 66),
                arrowprops=dict(facecolor=PALETTE["accent"], edgecolor=PALETTE["accent"], arrowstyle="->", lw=1.2),
                ha="center", va="bottom", color=PALETTE["text_secondary"], fontsize=7.5)

    # Web -> Process
    ax.annotate("Sanitized Evidence Text", xy=(63, 60), xytext=(77, 60),
                arrowprops=dict(facecolor=PALETTE["accent_2"], edgecolor=PALETTE["accent_2"], arrowstyle="->", lw=1.2),
                ha="center", va="top", color=PALETTE["text_secondary"], fontsize=7.5)

    # Process -> DB
    ax.annotate("Persist Telemetry & Citations", xy=(48, 29), xytext=(48, 50),
                arrowprops=dict(facecolor=PALETTE["accent"], edgecolor=PALETTE["accent"], arrowstyle="->", lw=1.2),
                ha="right", va="center", color=PALETTE["text_secondary"], fontsize=7.5)

    # DB -> Process
    ax.annotate("Read Historical Metrics", xy=(52, 50), xytext=(52, 29),
                arrowprops=dict(facecolor=PALETTE["accent_2"], edgecolor=PALETTE["accent_2"], arrowstyle="->", lw=1.2),
                ha="left", va="center", color=PALETTE["text_secondary"], fontsize=7.5)

    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig.savefig(save_path)
    plt.close(fig)
    print(f"Generated DFD Level 0: {save_path}")


if __name__ == "__main__":
    generate_architecture_block_diagram()
    generate_dfd_level_0()
