# aidy.AI System Architecture & Design Documentation

## 1. System Overview
**aidy.AI** is an autonomous multi-agent intelligence platform engineered to execute end-to-end research, source grounding, claim verification, and formal reporting. The architecture adheres to a clean layered design separating user interaction, multi-agent orchestration, external tool gateways, and persistence.

---

## 2. System Block Diagram

```mermaid
flowchart TD
    subgraph UI ["Presentation Layer (Streamlit)"]
        UI_Dash["Overview Dashboard"]
        UI_New["New Research Inquiry"]
        UI_Live["Live Workspace (Real-time Timeline)"]
        UI_Reports["Reports Library (Draft / Final Review)"]
        UI_Analytics["Agent Analytics (Plotly)"]
        UI_Data["Dataset Explorer & Audit"]
        UI_Eval["Evaluation Center"]
    end

    subgraph Orchestration ["Orchestration Layer (CrewAI & Workflow Engine)"]
        Runner["ResearchWorkflowRunner"]
        Crew["CrewAI Sequential Process"]
        A_Research["Researcher Agent"]
        A_Fact["Fact-Checker Agent"]
        A_Analyst["Analyst Agent"]
        A_Writer["Writer Agent"]
    end

    subgraph Tools ["Tools & Security Gateway"]
        SearchTool["Web Search (SerpAPI / Tavily / Demo Cache)"]
        WebReader["Safe Webpage Reader (BeautifulSoup)"]
        SSRF_FW["SSRF Firewall & Content Sanitizer"]
        Registry["Source Registry (Deduplication & IDs)"]
    end

    subgraph Persistence ["Persistence Layer (SQLAlchemy ORM)"]
        DB[(SQLite / PostgreSQL DB)]
        M_Run["ResearchRunModel"]
        M_Source["SourceModel"]
        M_Claim["ClaimModel"]
        M_Report["ReportModel"]
    end

    UI_New -->|ResearchQuery| Runner
    Runner --> Crew
    Crew --> A_Research --> A_Fact --> A_Analyst --> A_Writer
    A_Research --> SearchTool
    A_Research --> WebReader
    WebReader --> SSRF_FW
    SearchTool --> Registry
    WebReader --> Registry
    A_Fact --> Registry
    A_Writer --> Registry
    Runner -->|Save Execution Graph| Persistence
    Persistence --> UI_Reports
    Persistence --> UI_Analytics
    Persistence --> UI_Dash
```

---

## 3. Data Flow Diagram (DFD Level 0 — Context Level)

```mermaid
flowchart LR
    User(["Specialist / Researcher"])
    System[["aidy.AI Multi-Agent Platform (P0)"]]
    Web[("External Web & Academic Indices")]
    DB[("SQLite Storage (D1)")]

    User -->|1. Research Query & Constraints| System
    System -->|2. Search & Fetch Requests| Web
    Web -->|3. Raw Webpages & Search Results| System
    System -->|4. Persist Runs, Citations & Draft Reports| DB
    DB -->|5. Retrieve Stored Reports & Analytics| System
    System -->|6. Audit-Grade Report with Traceable Citations| User
    User -->|7. Editorial Approval & Finalization| System
```

---

## 4. Multi-Agent Sequential Workflow

The orchestrated execution progresses through a deterministic, fail-safe 7-stage pipeline:

```mermaid
sequenceDiagram
    autonumber
    actor User as Human Researcher
    participant Coord as Workflow Runner
    participant Res as Researcher Agent
    participant Fact as Fact-Checker Agent
    participant Ana as Analyst Agent
    participant Wri as Writer Agent
    participant DB as Persistence Layer

    User->>Coord: Dispatch ResearchQuery(Topic, Depth, MaxSources)
    Coord->>Res: Deconstruct Topic & Retrieve External Evidence
    Res->>Res: Query Search API & Sanitize Web Content
    Res-->>Coord: Numbered Sources ([1], [2]) & Evidence Snippets
    Coord->>Fact: Audit Factual Statements Against Primary Text
    Fact->>Fact: Classify Claims (Verified / Contradicted / Unverified)
    Fact-->>Coord: Verified Claim Matrix with Rationales
    Coord->>Ana: Synthesize Patterns, Contradictions & Gaps
    Ana-->>Coord: Analytical Synthesis Document
    Coord->>Wri: Compile 10-Section Formal Report with Bracketed Citations
    Wri-->>Coord: Markdown Research Report
    Coord->>DB: Atomic Transaction (Run, Sources, Claims, Draft Report)
    Coord-->>User: Display Live Workspace with Draft Report
    User->>Coord: Editorial Review -> Update Status to Final & Export PDF
```

---

## 5. Entity-Relationship (Data Model) Diagram

```mermaid
erDiagram
    RESEARCH_RUNS ||--o{ SOURCES : contains
    RESEARCH_RUNS ||--o{ CLAIMS : evaluates
    RESEARCH_RUNS ||--|| REPORTS : produces

    RESEARCH_RUNS {
        string run_id PK "Unique Run ID (e.g. RUN-ABC12345)"
        string topic "Central Research Question"
        datetime created_at "UTC Timestamp"
        float duration_s "Total Execution Seconds"
        int tokens_used "Total LLM Tokens Expended"
        float quality_score "Standardized Quality Score"
        int errors "Count of Retries/Errors Encountered"
        string status "completed / failed"
        boolean is_offline_demo "Flag for Offline Data"
    }

    SOURCES {
        int id PK "Autoincrement Primary Key"
        string run_id FK "References research_runs.run_id"
        int citation_id "Numeric Identifier ([1], [2]...)"
        string title "Webpage or Paper Title"
        string url "Canonical Normalized URL"
        string snippet "Extracted Evidence Quote"
        string domain "Authority Domain"
        string published_date "Publication Date"
        boolean is_verified "Corroborated by Fact-Checker"
    }

    CLAIMS {
        int id PK "Autoincrement Primary Key"
        string run_id FK "References research_runs.run_id"
        string claim_id "Claim Tag (e.g. C01, C02)"
        string statement "Core Factual Proposition"
        string verification_status "Verified / Contradicted / Unverified"
        string supporting_citations "JSON array of citation IDs"
        string rationale "Audit Justification"
        float confidence "Confidence Metric [0.0 - 1.0]"
    }

    REPORTS {
        string report_id PK "Unique Report ID (e.g. REP-2026-001)"
        string run_id FK "References research_runs.run_id"
        string topic "Title of Research Document"
        datetime created_at "Creation Timestamp"
        string executive_summary "High-Level Executive Summary"
        string markdown_content "Full 10-Section Markdown"
        string review_status "draft / reviewed / final"
        string reviewer_notes "Human Reviewer Comments"
    }
```

---

## 6. Component Explanations

1. **ResearchWorkflowRunner (`src/aidy/crew/workflow.py`):** Central coordinator controlling execution budgets, event callbacks to the UI, deterministic fallback triggers, and multi-agent task handoffs.
2. **SourceRegistry (`src/aidy/tools/source_registry.py`):** Thread-safe in-memory registry enforcing URL normalization, deduplication, and sequential citation numbering (`[1]`, `[2]`, ...).
3. **Security Firewall (`src/aidy/core/security.py`):** Protects the host system against SSRF by disallowing localhost, RFC 1918 private ranges, and cloud metadata endpoints. Defuses prompt-injection strings inside external HTML.
4. **Report Exporters (`src/aidy/export/`):** Converts structured Pydantic report schemas into clean Markdown and styled ReportLab PDFs in the aidy.AI brand palette.
5. **Database Repositories (`src/aidy/persistence/`):** Implements the Repository Pattern via SQLAlchemy ORM, decoupling database access from business logic.
