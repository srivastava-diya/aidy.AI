"""Validation module for agent activity datasets."""

from typing import Dict, List, Tuple
import pandas as pd
import numpy as np


EXPECTED_COLUMNS = [
    "run_id",
    "agent_role",
    "task_type",
    "tokens_used",
    "duration_s",
    "quality_score",
    "errors",
]

ALLOWED_AGENT_ROLES = {"Researcher", "Fact_Checker", "Analyst", "Writer", "Editor", "Publisher"}


def validate_schema(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Checks whether the dataframe contains all required columns and valid data types."""
    issues = []
    missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing_cols:
        issues.append(f"Missing columns: {missing_cols}")

    if "tokens_used" in df.columns and not pd.api.types.is_numeric_dtype(df["tokens_used"]):
        issues.append("Column 'tokens_used' is not numeric")

    if "duration_s" in df.columns and not pd.api.types.is_numeric_dtype(df["duration_s"]):
        issues.append("Column 'duration_s' is not numeric")

    if "quality_score" in df.columns and not pd.api.types.is_numeric_dtype(df["quality_score"]):
        issues.append("Column 'quality_score' is not numeric")

    if "errors" in df.columns and not pd.api.types.is_numeric_dtype(df["errors"]):
        issues.append("Column 'errors' is not numeric")

    return len(issues) == 0, issues


def check_ranges(df: pd.DataFrame) -> Dict[str, int]:
    """Identifies rows where values fall outside logical biological/system bounds."""
    violations = {}
    if "quality_score" in df.columns:
        violations["quality_out_of_bounds"] = int(((df["quality_score"] < 0.0) | (df["quality_score"] > 1.0)).sum())
    if "duration_s" in df.columns:
        violations["negative_duration"] = int((df["duration_s"] < 0).sum())
    if "tokens_used" in df.columns:
        violations["negative_tokens"] = int((df["tokens_used"] < 0).sum())
    if "errors" in df.columns:
        violations["negative_errors"] = int((df["errors"] < 0).sum())
    return violations


def detect_outliers_iqr(df: pd.DataFrame, column: str, k: float = 1.5) -> pd.Series:
    """Calculates outlier mask using Interquartile Range (IQR)."""
    if column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
        return pd.Series(False, index=df.index)
    q25 = df[column].quantile(0.25)
    q75 = df[column].quantile(0.75)
    iqr = q75 - q25
    lower_bound = q25 - k * iqr
    upper_bound = q75 + k * iqr
    return (df[column] < lower_bound) | (df[column] > upper_bound)
