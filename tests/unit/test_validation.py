"""Unit tests for dataset schema validation and boundary checks."""

import pandas as pd
import pytest
from aidy.data.validation import validate_schema, check_ranges, detect_outliers_iqr


def test_valid_schema():
    df = pd.DataFrame({
        "run_id": ["R001", "R002"],
        "agent_role": ["Researcher", "Writer"],
        "task_type": ["HealthAI", "FinTech"],
        "tokens_used": [1200, 3500],
        "duration_s": [45.2, 88.1],
        "quality_score": [0.85, 0.92],
        "errors": [0, 1],
    })
    is_valid, issues = validate_schema(df)
    assert is_valid is True
    assert len(issues) == 0


def test_invalid_schema_missing_column():
    df = pd.DataFrame({
        "run_id": ["R001"],
        "agent_role": ["Researcher"],
        "task_type": ["HealthAI"],
    })
    is_valid, issues = validate_schema(df)
    assert is_valid is False
    assert any("Missing columns" in iss for iss in issues)


def test_range_violations():
    df = pd.DataFrame({
        "tokens_used": [-50, 100],
        "duration_s": [10.0, -5.0],
        "quality_score": [1.5, 0.8],
        "errors": [-1, 0],
    })
    violations = check_ranges(df)
    assert violations["quality_out_of_bounds"] == 1
    assert violations["negative_duration"] == 1
    assert violations["negative_tokens"] == 1
    assert violations["negative_errors"] == 1


def test_iqr_outlier_detection():
    # 9 normal numbers and 1 extreme outlier
    data = [10, 12, 11, 10, 13, 11, 12, 10, 11, 1000]
    df = pd.DataFrame({"tokens_used": data})
    outliers = detect_outliers_iqr(df, "tokens_used", k=1.5)
    assert outliers.iloc[-1] == True
    assert outliers.iloc[0] == False
