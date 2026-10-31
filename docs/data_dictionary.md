# aidy.AI Data Dictionary & Schema Documentation

## 1. Overview
The primary evaluation and benchmarking dataset (`dataset.csv`) contains execution logs from autonomous multi-agent research workflows. Each row captures the operational profile, token consumption, runtime, and output quality score of a specialized agent executing a subtask within an orchestrated research run.

---

## 2. Core Schema Definition

| Column Name | Data Type | Nullable | Valid Range | Example Values | Description & Semantics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `run_id` | `VARCHAR(16)` | No | Pattern `R\d{3}` (`R001` - `R200`) | `R111`, `R132`, `R052` | Alphanumeric identifier linking collaborative agent tasks belonging to the same orchestrated research pipeline. |
| `agent_role` | `VARCHAR(32)` | No | `Researcher`, `Fact_Checker`, `Analyst`, `Writer`, `Editor`, `Publisher` | `Writer`, `Researcher`, `Fact_Checker` | Specialized autonomous persona assigned to execute the pipeline stage. |
| `task_type` | `VARCHAR(32)` | No | `AI_Trends`, `Market_Analysis`, `HealthAI`, `Climate_Tech`, `FinTech` | `AI_Trends`, `HealthAI` | Domain topic or research subject boundary guiding tool usage and context retrieval. |
| `tokens_used` | `INTEGER` | No | `507` to `7,996` tokens | `1845`, `7330`, `7254` | Combined prompt input and generated completion token expenditure measured across the LLM call. |
| `duration_s` | `FLOAT` | No | `5.6` to `119.9` seconds | `59.2`, `101.3`, `84.4` | Elapsed clock time from task dispatch to final structured response delivery. |
| `quality_score` | `FLOAT` | No | `0.600` to `1.000` | `0.890`, `0.897`, `0.718` | Normalized benchmark score assessing factual grounding, citation accuracy, coherence, and constraint fulfillment. |
| `errors` | `INTEGER` | No | `0` to `2` | `0`, `1`, `2` | Count of retries, network timeout recoveries, or format repair attempts triggered during agent execution. |

---

## 3. Derived & Enriched Columns (Cleaned Dataset: `dataset_cleaned.csv`)

| Column Name | Data Type | Nullable | Valid Range | Description |
| :--- | :--- | :--- | :--- | :--- |
| `is_outlier` | `BOOLEAN` | No | `True` / `False` | Flag indicating whether tokens, duration, or quality fall outside 2.0x Interquartile Range (IQR). Retained for statistical fidelity. |
| `anomaly_flag` | `BOOLEAN` | No | `True` / `False` | Operational warning flag indicating either `errors >= 1` or `quality_score < 0.65`. |
| `quality_per_minute` | `FLOAT` | No | `0.30` to `10.50` | Operational efficiency ratio: `quality_score / (duration_s / 60.0)`. |

---

## 4. Schema Discrepancy Reconciliation

During initial inspection of the supplied project resources, a minor divergence was identified between the Project Brief textual summary and the actual supplied `dataset.csv`:

| Field in Project Brief Text | Corresponding Field in `dataset.csv` | Resolution & Architecture Decision |
| :--- | :--- | :--- |
| `run_id` | `run_id` | Exact match. Kept as primary run identifier. |
| `agent_role` | `agent_role` | Exact match. |
| `task_description` | `task_type` | In `dataset.csv`, high-level categorical domains (`HealthAI`, `Market_Analysis`, etc.) are captured under `task_type`. aidy.AI preserves `task_type` while supporting detailed prompt descriptions in runtime models. |
| `tool_used` | Embedded in `agent_role` | In the benchmark dataset, tools map directly to agent roles (`Researcher` -> Web Search/Reader; `Fact_Checker` -> Citation Verifier). aidy.AI runtime logs explicit tool names (`SerpAPI`, `WebScraper`, `CitationVerifier`). |
| `input_tokens` / `output_tokens` | `tokens_used` | Summed into unified `tokens_used`. The runtime database model tracks prompt, completion, and total tokens separately. |
| `duration_s` | `duration_s` | Exact match. |
| `quality_score` | `quality_score` | Exact match. |
| *(Omitted in Brief text)* | `errors` | Explicitly present in CSV. Crucial for measuring reliability, retries, and failure rates. Fully preserved. |

This alignment ensures backwards compatibility with historical benchmark datasets while supporting rich, granular telemetry in live production executions.
