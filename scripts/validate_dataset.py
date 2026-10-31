"""Script to execute dataset validation and cleaning pipeline."""

import json
from aidy.data.cleaning import clean_dataset
from aidy.data.metrics import compute_dataset_metrics


def main():
    print("--- Starting aidy.AI Dataset Validation & Cleaning ---")
    df_cleaned, report = clean_dataset(
        input_path="data/raw/dataset.csv",
        output_path="data/processed/dataset_cleaned.csv",
    )

    metrics = compute_dataset_metrics(df_cleaned)

    print(f"Cleaned dataset saved: {len(df_cleaned)} rows, {df_cleaned.shape[1]} columns.")
    print(f"Schema status: {'Valid' if len(report['schema_issues']) == 0 else report['schema_issues']}")
    print(f"Missing values detected: {report['total_missing']}")
    print(f"Outliers flagged (IQR k=2.0): {report['outliers_flagged']}")
    print(f"Anomalies flagged: {report['anomalies_flagged']}")
    print(f"Mean duration: {metrics['mean_duration_s']}s | Mean quality: {metrics['mean_quality_score']} | Mean tokens: {metrics['mean_tokens_used']}")
    print(f"Overall error rate: {metrics['error_rate'] * 100:.2f}% | Completion rate: {metrics['task_completion_rate'] * 100:.2f}%")

    with open("data/processed/validation_report.json", "w", encoding="utf-8") as f:
        json.dump({"report": report, "metrics": metrics}, f, indent=2)

    print("Audit report written to data/processed/validation_report.json")


if __name__ == "__main__":
    main()
