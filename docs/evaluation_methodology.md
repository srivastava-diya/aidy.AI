# aidy.AI Evaluation Methodology & Telemetry Specification

## 1. Overview
The aidy.AI platform employs a dual evaluation framework:
1. **Offline Empirical Benchmarking:** Statistical profiling and anomaly detection over the historical 500-record dataset (`dataset.csv`).
2. **Online Runtime Evaluation:** Dynamic telemetry measuring factual alignment, citation coverage, execution latency, and error incidence during live agent execution.

---

## 2. Metric Formulations and Calculations

### 2.1 Quality Score ($Q$)
In the empirical benchmark dataset, `quality_score` represents a normalized index $\in [0.0, 1.0]$. In live research workflows, quality is computed based on citation grounding fidelity and format completeness:
$$Q = 0.5 \times C_{\text{coverage}} + 0.3 \times F_{\text{structure}} + 0.2 \times (1 - E_{\text{error\_penalty}})$$
Where:
- $C_{\text{coverage}}$: Fraction of factual claims directly anchored to a verified citation index ($N_{\text{verified}} / N_{\text{claims}}$).
- $F_{\text{structure}}$: Fulfillment of all 10 required report sections (binary 1.0 if all present, discounted if sections are omitted).
- $E_{\text{error\_penalty}}$: Deduction applied for network timeouts or schema repair attempts ($0.15$ per retry).

### 2.2 Execution Duration ($D$)
Total elapsed wall-clock time in seconds from initial user dispatch to final report serialization:
$$D = t_{\text{completed}} - t_{\text{dispatched}}$$

### 2.3 Citation Coverage Ratio ($CCR$)
The proportion of key empirical claims in the research report that are explicitly linked to an existing primary source reference:
$$CCR = \frac{\sum_{i=1}^{M} \mathbb{I}(\text{Claim}_i \text{ has valid } [k])}{M} \times 100\%$$
*Acceptance Criterion:* $CCR \ge 90\%$. aidy.AI achieves 100% in automated evaluation tests.

### 2.4 Error Occurrence Rate ($ERR$)
Proportion of multi-agent tasks encountering execution exceptions or requiring automated retry logic:
$$ERR = \frac{\sum \mathbb{I}(\text{Errors} > 0)}{N_{\text{total}}} \times 100\%$$
*Baseline Dataset Measurement:* $8.40\%$ ($42 / 500$ runs had 1 or 2 errors).

---

## 3. Metric Limitations and Caveats

1. **Non-Causality of Observational Data:** As demonstrated in EDA Plot 2, execution duration does not correlate with quality ($r = 0.021$). Longer runtimes often reflect API latency or retry timeouts rather than deeper reasoning.
2. **Context Window Saturation:** High token consumption beyond 15,000 tokens does not guarantee higher quality; prompt verbosity can dilute evidence focus.
3. **Synthetic Dataset Provenance:** The 4,500 synthetic records generated in `data/generated/synthetic_dataset_5000.csv` must be interpreted as simulated stress-testing data rather than empirical measurements.
