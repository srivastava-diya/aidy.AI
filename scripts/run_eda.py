"""Automated execution script for Exploratory Data Analysis and diagram generation."""

import sys
import json
sys.stdout.reconfigure(encoding='utf-8')
from aidy.data.loader import load_cleaned_dataset
from aidy.analytics.eda import run_full_eda
from aidy.analytics.visualizations import generate_all_eda_visualizations


def main():
    print("--- Running aidy.AI Exploratory Data Analysis (EDA) ---")
    df = load_cleaned_dataset("data/processed/dataset_cleaned.csv")
    print(f"Loaded {len(df)} records from cleaned dataset.")

    eda_results = run_full_eda(df)
    print("\n--- Key Statistical Insights ---")
    for ins in eda_results["interpretations"]:
        print(f"* {ins}")

    print("\n--- Generating Static Figures for Synopsis and Report ---")
    plots = generate_all_eda_visualizations(df, output_dir="docs/diagrams")
    for p in plots:
        print(f"Saved: {p}")

    with open("docs/diagrams/eda_summary.json", "w", encoding="utf-8") as f:
        json.dump(eda_results, f, indent=2)

    print("\nEDA Completed successfully. Artifacts available in docs/diagrams/")


if __name__ == "__main__":
    main()
