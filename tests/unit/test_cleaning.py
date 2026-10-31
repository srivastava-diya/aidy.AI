"""Unit tests for dataset cleaning and preprocessing."""

import os
import pandas as pd
import pytest
from aidy.data.cleaning import clean_dataset


def test_clean_dataset_execution(tmp_path):
    raw_csv = tmp_path / "raw.csv"
    cleaned_csv = tmp_path / "cleaned.csv"

    df_test = pd.DataFrame({
        "run_id": [" R001 ", "R002"],
        "agent_role": ["Researcher", "Editor"],
        "task_type": [" HealthAI ", "FinTech"],
        "tokens_used": ["1500", "4200"],
        "duration_s": ["45.5", "60.0"],
        "quality_score": ["0.88", "1.5"],  # 1.5 should be clipped to 1.0
        "errors": ["0", "1"],
    })
    df_test.to_csv(raw_csv, index=False)

    df_cleaned, report = clean_dataset(str(raw_csv), str(cleaned_csv))

    assert len(df_cleaned) == 2
    assert df_cleaned["run_id"].iloc[0] == "R001"
    assert df_cleaned["task_type"].iloc[0] == "HealthAI"
    assert df_cleaned["quality_score"].iloc[1] == 1.0  # Clipped
    assert "is_outlier" in df_cleaned.columns
    assert "anomaly_flag" in df_cleaned.columns
    assert os.path.exists(cleaned_csv)
