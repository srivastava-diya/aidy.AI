"""Unit tests for statistical metrics calculations."""

import pandas as pd
from aidy.data.metrics import compute_dataset_metrics


def test_compute_dataset_metrics():
    df = pd.DataFrame({
        "run_id": ["R01", "R02", "R03", "R04"],
        "agent_role": ["Researcher", "Researcher", "Writer", "Fact_Checker"],
        "task_type": ["HealthAI", "HealthAI", "FinTech", "FinTech"],
        "tokens_used": [1000, 2000, 3000, 4000],
        "duration_s": [10.0, 20.0, 30.0, 40.0],
        "quality_score": [0.80, 0.90, 0.70, 0.60],
        "errors": [0, 0, 1, 0],
    })

    metrics = compute_dataset_metrics(df)
    assert metrics["total_records"] == 4
    assert metrics["mean_duration_s"] == 25.0
    assert metrics["median_duration_s"] == 25.0
    assert metrics["mean_quality_score"] == 0.75
    assert metrics["mean_tokens_used"] == 2500.0
    assert metrics["total_errors"] == 1
    assert metrics["runs_with_errors"] == 1
    assert metrics["error_rate"] == 0.25
    assert len(metrics["by_agent_role"]) == 3
