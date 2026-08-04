import os

import streamlit as st

from src.data_loader import load_trial_balance
from src.validation import validate_trial_balance

st.set_page_config(
    page_title="Moroccan Financial Statement Analyzer",
    layout="wide"
)

st.title("Moroccan Financial Statement Analyzer")

st.warning(
    "Prototype for educational purposes only. "
    "This tool does not replace professional financial analysis, "
    "audit judgment, or advisory work."
)

st.info(
    "Moroccan statutory financial statements are generally prepared using historical cost. "
    "Book values may differ from economic values."
)

st.subheader("Slice 1 — Trial balance loading and validation")

uploaded_file = st.file_uploader(
    "Upload trial balance CSV",
    type=["csv"]
)

trial_balance = None
source_name = None

if uploaded_file is not None:
    trial_balance = load_trial_balance(uploaded_file)
    source_name = uploaded_file.name

elif os.path.exists("data/sample_trial_balance.csv"):
    trial_balance = load_trial_balance("data/sample_trial_balance.csv")
    source_name = "data/sample_trial_balance.csv"

if trial_balance is None:
    st.info(
        "No trial balance found. "
        "Please upload a CSV file or create data/sample_trial_balance.csv."
    )

else:
    st.success(f"Loaded: {source_name}")

    st.subheader("Raw trial balance")
    st.dataframe(trial_balance)

    validation = validate_trial_balance(trial_balance)

    st.subheader("Balance validation")
    st.dataframe(validation)

    if validation["balanced"].all():
        st.success("The trial balance is balanced for all years.")
    else:
        st.error("The trial balance is not balanced for all years.")