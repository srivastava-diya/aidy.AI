# ✦ aidy.AI

> **Research, verified.** A multi-agent research assistant where every claim is fact-checked against a cited primary source.

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![CrewAI](https://img.shields.io/badge/Orchestration-CrewAI-8B5CF6.svg)](https://www.crewai.com/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red.svg)](https://streamlit.io/)

---

## Why aidy.AI

Single-prompt LLMs fabricate citations and state hallucinations as fact. aidy.AI splits the work across a crew of specialised agents, orchestrated with **CrewAI**:

1. **Researcher** — breaks the question into objectives, queries search providers, and collects primary evidence while blocking malicious URLs and SSRF vectors.
2. **Fact-Checker** — an adversarial auditor that labels every assertion `Verified`, `Contradicted`, or `Unverified` against primary text.
3. **Analyst** — synthesises across sources: consensus, tensions, and open research gaps.
4. **Writer** — assembles a structured 10-section report with bracketed citations (`[1]`, `[2]`).
5. **Human in the loop** — reports start as `draft` and need specialist approval before they're final.

## Features

- **Paper & ink UI** — a warm editorial interface: Instrument Serif headings, mono labels, ledger tables, and rubber-stamp verdicts on fact-checked claims.
- **Auditable citations** — deduplication, canonical URL normalisation, and sequential reference indexing.
- **Claim verification matrix** — sentence-level audit exposing unsupported assertions before compilation.
- **Defense in depth** — SSRF firewall for private IP space (`localhost`, `10.0.0.0/8`, `192.168.0.0/16`, `169.254.169.254`) and prompt-injection defusing for fetched HTML.
- **Analytics suite** — EDA over a 500-run dataset, interactive Plotly charts, data dictionary, and a 5,000-row synthetic expansion.
- **Export** — GitHub-flavoured Markdown and styled PDF.

## Stack

| Layer | Tech |
| :--- | :--- |
| Frontend | Streamlit, Plotly, custom CSS (`src/aidy/ui/theme.py`, `.streamlit/config.toml`) |
| Agents | CrewAI, Pydantic v2, BeautifulSoup4, Requests |
| Persistence | SQLAlchemy (SQLite by default, PostgreSQL-ready) |
| Export | ReportLab, Matplotlib |
| Tests | Pytest |

## Architecture

```
Streamlit UI (paper & ink theme)
       │
ResearchWorkflowRunner  ── status callbacks ──> Live Workspace
       │
CrewAI sequential pipeline
 ├── Researcher    ──> web search + safe page reader
 ├── Fact-Checker  ──> source registry + claim audit
 ├── Analyst       ──> cross-source synthesis
 └── Writer        ──> 10-section report
       │
       ├──> SQL database (runs, sources, claims, reports)
       └──> Markdown / PDF exporters
```

## Getting started

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env   # optional — see below
streamlit run app.py
```

Open `http://localhost:8501`.

## Environment variables

**None are required.** With an empty `.env`, aidy.AI runs in deterministic **offline demo mode** against curated benchmark sources — the full pipeline, fact-checking, and exports all work at zero cost.

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `SERPAPI_API_KEY` | — | Enables live Google search via SerpAPI. **Setting this (or Tavily) switches to live mode.** |
| `TAVILY_API_KEY` | — | Alternative live search provider (used if SerpAPI is unset or fails). |
| `SEARCH_PROVIDER` | `serpapi` | Label only (logged); provider is chosen by which key is set. |
| `OPENAI_API_KEY` | — | Reserved for the CrewAI agents. The current workflow is deterministic and does not call an LLM yet; this key only affects the status shown in the UI. |
| `OPENAI_MODEL_NAME` | `gpt-4o-mini` | OpenAI model id (reserved). |
| `ANTHROPIC_API_KEY` / `GEMINI_API_KEY` | — | Alternative LLM providers (reserved). |
| `REQUEST_TIMEOUT_S` | `15` | HTTP timeout for search and page fetches. |
| `MAX_SEARCH_RESULTS` | `5` | Results per search query. |
| `MAX_TOKENS_PER_RUN` | `25000` | Token budget per run. |
| `DATABASE_URL` | `sqlite:///data/aidy.db` | Any SQLAlchemy URL, e.g. `postgresql://user:pass@host:5432/aidy`. |
| `REPORTS_DIR` | `data/reports` | Where exported reports are written. |

## Views

1. **Overview** — KPIs, how it works, recent runs.
2. **New Research** — question, sub-questions, depth, and source limits.
3. **Live Workspace** — live progress, sources, claim audit, synthesis, and draft report.
4. **Reports** — review, edit, approve (`draft → reviewed → final`), export `.md` / `.pdf`.
5. **Analytics** — quality, latency, token, and error charts by agent role.
6. **Datasets** — raw vs. cleaned data, data dictionary, cleaning audit, CSV downloads.
7. **Evaluation** — benchmark suite for citation coverage and claim fidelity.
8. **Settings** — provider status and execution budgets.

## Data pipelines & tests

```powershell
$env:PYTHONPATH="src"
python scripts/validate_dataset.py         # -> data/processed/dataset_cleaned.csv, validation_report.json
python scripts/run_eda.py                  # -> docs/diagrams/eda_plot*.png
python scripts/generate_synthetic_data.py  # -> data/generated/synthetic_dataset_5000.csv
pytest -v
```

## Project layout

```
app.py                  Streamlit entry point
src/aidy/               application package (agents, crew, tools, data, export, persistence, ui)
data/raw|processed|generated
docs/                   architecture, security, evaluation, user guide, diagrams
notebooks/              EDA notebook
scripts/                data + diagram generation
tests/                  unit, integration, evaluation
```

---

Built for the HCLTech Career Shaper Programme (Project 78: Multi-Agent Research Assistant with CrewAI), 2025–26.
