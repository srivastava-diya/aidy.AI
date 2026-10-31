"""Dataset loading utilities for raw and cleaned datasets."""

import os
import pandas as pd
from typing import Optional


RAW_DATASET_PATH = "data/raw/dataset.csv"
CLEANED_DATASET_PATH = "data/processed/dataset_cleaned.csv"
SYNTHETIC_DATASET_PATH = "data/generated/synthetic_dataset_5000.csv"


def load_raw_dataset(path: str = RAW_DATASET_PATH) -> pd.DataFrame:
    """Loads raw dataset without modifications."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Raw dataset not found at {path}")
    return pd.read_csv(path)


def load_cleaned_dataset(path: str = CLEANED_DATASET_PATH) -> pd.DataFrame:
    """Loads preprocessed and validated dataset."""
    if not os.path.exists(path):
        from aidy.data.cleaning import clean_dataset
        df, _ = clean_dataset(RAW_DATASET_PATH, path)
        return df
    return pd.read_csv(path)


def load_synthetic_dataset(path: str = SYNTHETIC_DATASET_PATH) -> Optional[pd.DataFrame]:
    """Loads expanded synthetic dataset if available."""
    if os.path.exists(path):
        return pd.read_csv(path)
    return None
