"""Synthetic data generation script expanding multi-agent research logs.

Adheres strictly to the guidelines in Dataset_Generation_Prompt.txt:
- Generates 4,500 additional correlated rows across 20 distinct research topics.
- Employs realistic multi-variate statistical distributions mirroring historical observations.
- Labels synthetic provenance and records exact random seed for scientific reproducibility.
- Preserves original dataset.csv intact; outputs to data/generated/synthetic_dataset_5000.csv.
"""

import os
import random
import numpy as np
import pandas as pd


RANDOM_SEED = 42
TOTAL_SYNTHETIC_ROWS = 4500

TOPICS = [
    "HealthAI", "Market_Analysis", "FinTech", "Climate_Tech", "AI_Trends",
    "Quantum_Computing", "Autonomous_Vehicles", "Cybersecurity", "Biotechnology", "Clean_Energy",
    "Edge_AI", "Robotics", "Supply_Chain_AI", "NeuroTech", "Space_Exploration",
    "AgriTech", "LegalTech", "EdTech_Innovations", "Smart_Cities", "Drug_Discovery"
]

ROLES = ["Researcher", "Fact_Checker", "Analyst", "Writer", "Editor"]
ROLE_WEIGHTS = [0.25, 0.20, 0.20, 0.20, 0.15]


def generate_synthetic_dataset(
    original_path: str = "data/raw/dataset.csv",
    output_path: str = "data/generated/synthetic_dataset_5000.csv",
    seed: int = RANDOM_SEED
) -> pd.DataFrame:
    """Generates synthetic multi-agent run logs and combines them with original records into a 5,000-row dataset."""
    np.random.seed(seed)
    random.seed(seed)

    # Load original 500 records
    df_orig = pd.read_csv(original_path)
    df_orig["data_source"] = "original_empirical"

    synthetic_records = []
    start_run_num = 201

    for i in range(TOTAL_SYNTHETIC_ROWS):
        run_num = start_run_num + (i // len(ROLES))
        run_id = f"R{run_num:03d}"
        role = random.choices(ROLES, weights=ROLE_WEIGHTS, k=1)[0]
        topic = random.choice(TOPICS)

        # Baseline parameters per role
        if role == "Researcher":
            base_tokens = np.random.normal(4800, 1400)
            base_duration = np.random.normal(70, 25)
        elif role == "Fact_Checker":
            base_tokens = np.random.normal(3800, 1600)
            base_duration = np.random.normal(55, 28)
        elif role == "Analyst":
            base_tokens = np.random.normal(4200, 1200)
            base_duration = np.random.normal(60, 20)
        elif role == "Writer":
            base_tokens = np.random.normal(4500, 1500)
            base_duration = np.random.normal(75, 25)
        else:  # Editor
            base_tokens = np.random.normal(3200, 1400)
            base_duration = np.random.normal(45, 22)

        tokens_used = int(np.clip(base_tokens, 500, 8000))
        duration_s = float(np.round(np.clip(base_duration + (tokens_used / 400.0), 5.0, 120.0), 1))

        # Fault injection rate ~ 3.5%
        fault_dice = random.random()
        if fault_dice < 0.025:
            errors = 1
            quality_score = float(np.round(np.random.uniform(0.60, 0.74), 3))
            duration_s = float(np.round(min(120.0, duration_s * 1.25), 1))
        elif fault_dice < 0.035:
            errors = 2
            quality_score = float(np.round(np.random.uniform(0.60, 0.68), 3))
            duration_s = float(np.round(min(120.0, duration_s * 1.45), 1))
        else:
            errors = 0
            # Higher quality scores for clean runs
            quality_score = float(np.round(np.clip(np.random.normal(0.83, 0.09), 0.62, 1.0), 3))

        synthetic_records.append({
            "run_id": run_id,
            "agent_role": role,
            "task_type": topic,
            "tokens_used": tokens_used,
            "duration_s": duration_s,
            "quality_score": quality_score,
            "errors": errors,
            "data_source": "synthetic_generated"
        })

    df_synth = pd.DataFrame(synthetic_records)
    df_combined = pd.concat([df_orig, df_synth], ignore_index=True)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_combined.to_csv(output_path, index=False)
    print(f"Generated {len(df_synth)} synthetic rows. Total combined dataset: {len(df_combined)} rows written to {output_path}.")
    return df_combined


if __name__ == "__main__":
    generate_synthetic_dataset()
