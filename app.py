import streamlit as st

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

st.success("Environment setup OK with uv.")