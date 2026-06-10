import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="SocialMind AI",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 SocialMind AI")

st.markdown("""
### AI-Powered Social Intelligence Platform

Analyze public sentiment, identify risks,
detect topics and generate business recommendations.
""")

df = pd.read_csv(
    "data/processed/final_analyzed_data.csv"
)

col1,col2,col3 = st.columns(3)

col1.metric(
    "Records",
    len(df)
)

col2.metric(
    "Topics",
    df["topic"].nunique()
)

col3.metric(
    "Sources",
    df["source_type"].nunique()
)

st.success(
    "Use the sidebar to navigate through analytics modules."
)