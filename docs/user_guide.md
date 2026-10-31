# aidy.AI User Guide & Operational Manual

## 1. Quickstart Guide

### 1.1 Launching the Application
Execute the following command in PowerShell from the project root:
```powershell
python -m streamlit run app.py
```
Open your web browser at `http://localhost:8501`. The application will launch displaying the **Overview Dashboard** in the aidy.AI paper & ink interface.

---

## 2. Navigating the 8 Application Modules

### 2.1 Overview Dashboard
- **Key Metrics:** Review aggregate system telemetry including total runs, success rate, average quality score, and average latency.
- **Recent Research Runs:** Review previously executed research inquiries with direct links to generated reports.
- **Action:** Click **New Research Run** to launch an inquiry.

### 2.2 New Research
- **Topic Input:** Provide a clear research topic (e.g., *"Research the current applications, benefits, limitations, and future scope of Agentic AI in healthcare."*).
- **Subquestions:** Enter specific questions (one per line) to guide the Researcher Agent.
- **Investigation Depth:** Select between `Standard`, `Comprehensive`, or `Deep Dive`.
- **Max Sources:** Choose between 2 and 10 primary sources to retrieve and cross-reference.
- **Dispatch:** Click **Launch Multi-Agent Crew** to start execution.

### 2.3 Live Research Workspace
- **Progress Tracking:** Follow the real-time stage progress bar across all 7 pipeline stages.
- **Retrieved Sources Tab:** View all external sources with Title, Canonical URL, Domain, and Verified status.
- **Fact-Check Claim Audit Tab:** Inspect factual assertions evaluated by the Fact-Checker Agent, featuring color-coded status badges (`VERIFIED`, `CONTRADICTED`, `UNVERIFIED`) and supporting citation numbers.
- **Analytical Synthesis Tab:** Explore emerging technological patterns, institutional tensions, and research gaps identified by the Analyst Agent.
- **Generated Report Tab:** Preview the draft report with inline citations (`[1]`, `[2]`). Click **Open in Reports** to proceed to human review.

### 2.4 Reports
- **Report Selection:** Select any previously completed research report from the dropdown.
- **Editorial Approval:** Change the review status from `draft` to `reviewed` and `final`.
- **Markdown Editor:** Make inline adjustments to sections or add reviewer notes.
- **Exporting:** Download the report as a clean Markdown (`.md`) file or an editorial ReportLab PDF (`.pdf`).

### 2.5 Analytics
- **Role Performance:** View average quality, duration, and token consumption by agent role (`Researcher`, `Fact_Checker`, `Analyst`, `Writer`, `Editor`, `Publisher`).
- **Interactive Visualizations:** Explore Plotly charts for quality score distributions, duration vs. quality scatter plots, and token/error distributions.
- **Filters:** Filter analytics by specific agent roles or research domains (`HealthAI`, `FinTech`, `Climate_Tech`, `Market_Analysis`, `AI_Trends`).

### 2.6 Datasets
- **Previews:** Switch between Cleaned Dataset (500 rows), Raw Dataset (500 rows), and Synthetic Expansion (5,000 rows).
- **Data Dictionary:** Inspect column types, valid ranges, nullability, and descriptions.
- **Direct Downloads:** Download `dataset_cleaned.csv`, `data_dictionary.csv`, and `synthetic_dataset_5000.csv` directly to your local workstation.

### 2.7 Evaluation
- **Benchmark Suite:** Run automated evaluations across standardized research scenarios (`BENCH-01`, `BENCH-02`, `BENCH-03`).
- **Telemetry Verification:** Review measured citation coverage (100%), claim audit accuracy, and latency.

### 2.8 System Settings
- **Provider Status:** Check configuration status for OpenAI, SerpAPI, and Tavily without exposing raw API keys.
- **Budget Adjustments:** Adjust HTTP timeouts and token budgets per run.
- **Setup Guidance:** View instructions for configuring `.env` variables for live web search and dynamic LLM inference.
