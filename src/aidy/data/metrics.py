"""Metric calculation functions for dataset and runtime evaluations."""

from typing import Dict, Any
import pandas as pd
import numpy as np


def compute_dataset_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculates factual statistical metrics directly from the agent activity dataset."""
    total_runs = len(df)
    if total_runs == 0:
        return {}

    duration_mean = float(df["duration_s"].mean())
    duration_median = float(df["duration_s"].median())
    duration_std = float(df["duration_s"].std())

    quality_mean = float(df["quality_score"].mean())
    quality_median = float(df["quality_score"].median())
    quality_std = float(df["quality_score"].std())

    tokens_mean = float(df["tokens_used"].mean())
    tokens_median = float(df["tokens_used"].median())
    tokens_total = int(df["tokens_used"].sum())

    total_errors = int(df["errors"].sum())
    runs_with_errors = int((df["errors"] > 0).sum())
    error_rate = float(runs_with_errors / total_runs)

    # Success rate defined as runs with 0 errors and quality_score >= 0.70
    successful_runs = int(((df["errors"] == 0) & (df["quality_score"] >= 0.70)).sum())
    task_completion_rate = float(successful_runs / total_runs)

    # Aggregations by agent role
    role_metrics = (
        df.groupby("agent_role")
        .agg(
            runs=("run_id", "count"),
            avg_quality=("quality_score", "mean"),
            median_quality=("quality_score", "median"),
            avg_duration=("duration_s", "mean"),
            avg_tokens=("tokens_used", "mean"),
            error_count=("errors", "sum"),
            error_rate=("errors", lambda x: (x > 0).mean()),
        )
        .round(4)
        .reset_index()
        .to_dict(orient="records")
    )

    # Aggregations by task type
    task_metrics = (
        df.groupby("task_type")
        .agg(
            runs=("run_id", "count"),
            avg_quality=("quality_score", "mean"),
            avg_duration=("duration_s", "mean"),
            avg_tokens=("tokens_used", "mean"),
            error_count=("errors", "sum"),
        )
        .round(4)
        .reset_index()
        .to_dict(orient="records")
    )

    return {
        "total_records": total_runs,
        "mean_duration_s": round(duration_mean, 2),
        "median_duration_s": round(duration_median, 2),
        "std_duration_s": round(duration_std, 2),
        "mean_quality_score": round(quality_mean, 4),
        "median_quality_score": round(quality_median, 4),
        "std_quality_score": round(quality_std, 4),
        "mean_tokens_used": round(tokens_mean, 1),
        "median_tokens_used": round(tokens_median, 1),
        "total_tokens_used": tokens_total,
        "total_errors": total_errors,
        "runs_with_errors": runs_with_errors,
        "error_rate": round(error_rate, 4),
        "task_completion_rate": round(task_completion_rate, 4),
        "by_agent_role": role_metrics,
        "by_task_type": task_metrics,
    }
