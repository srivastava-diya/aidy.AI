"""Dataset Explorer page for inspecting raw, cleaned, and expanded datasets."""

import os
import streamlit as st
import pandas as pd
from aidy.data.loader import load_raw_dataset, load_cleaned_dataset, load_synthetic_dataset
from aidy.analytics.eda import run_full_eda
from aidy.ui.theme import page_header

DICTIONARY_PATH = "data/processed/data_dictionary_completed.csv"


def render_dataset_explorer_page():
    page_header(
        "Datasets",
        "Inspect the run-log dataset, its cleaning audit, and the data dictionary.",
        eyebrow="Data",
    )

    df_raw = load_raw_dataset()
    df_cleaned = load_cleaned_dataset()
    df_synth = load_synthetic_dataset()

    c_dl1, c_dl2, c_dl3 = st.columns(3)
    with c_dl1:
        st.download_button(
            label="Cleaned CSV",
            data=df_cleaned.to_csv(index=False),
            file_name="dataset_cleaned.csv",
            mime="text/csv",
            width="stretch",
        )
    with c_dl2:
        if os.path.exists(DICTIONARY_PATH):
            with open(DICTIONARY_PATH, "r", encoding="utf-8") as f:
                dict_text = f.read()
            st.download_button(
                label="Data dictionary",
                data=dict_text,
                file_name="data_dictionary.csv",
                mime="text/csv",
                width="stretch",
            )
    with c_dl3:
        if df_synth is not None:
            st.download_button(
                label="Synthetic 5k CSV",
                data=df_synth.to_csv(index=False),
                file_name="synthetic_dataset_5000.csv",
                mime="text/csv",
                width="stretch",
            )

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    tab_preview, tab_dict, tab_audit = st.tabs(["Preview", "Dictionary", "Cleaning audit"])

    with tab_preview:
        view_mode = st.radio(
            "Dataset",
            options=["Cleaned", "Raw", "Synthetic"],
            horizontal=True,
            label_visibility="collapsed",
        )
        if view_mode == "Cleaned":
            st.dataframe(df_cleaned, width="stretch")
            st.caption(f"{df_cleaned.shape[0]} rows × {df_cleaned.shape[1]} columns · derived: `is_outlier`, `anomaly_flag`, `quality_per_minute`")
        elif view_mode == "Raw":
            st.dataframe(df_raw, width="stretch")
            st.caption(f"{df_raw.shape[0]} rows × {df_raw.shape[1]} columns · original, unmodified")
        else:
            if df_synth is not None:
                st.dataframe(df_synth.head(500), width="stretch")
                st.caption(f"First 500 of {len(df_synth):,} rows across 20 topics")
            else:
                st.info("Synthetic dataset not yet generated. Run `make synthetic`.")

    with tab_dict:
        if os.path.exists(DICTIONARY_PATH):
            st.dataframe(pd.read_csv(DICTIONARY_PATH), width="stretch", hide_index=True)

    with tab_audit:
        eda_res = run_full_eda(df_cleaned)
        for ins in eda_res["interpretations"]:
            st.markdown(f"- {ins}")
