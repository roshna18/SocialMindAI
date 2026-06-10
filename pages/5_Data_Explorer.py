import streamlit as st
import pandas as pd

st.title("🔍 Data Explorer")

df = pd.read_csv(
    "data/processed/final_analyzed_data.csv"
)

source = st.selectbox(
    "Filter by Source",
    ["All"] + list(df["source_type"].unique())
)

if source != "All":

    df = df[
        df["source_type"] == source
    ]

st.dataframe(
    df,
    use_container_width=True
)