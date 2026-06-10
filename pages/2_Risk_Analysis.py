import streamlit as st
import pandas as pd
import plotly.express as px

st.title("⚠ Risk Analysis")

risk_df = pd.read_csv(
    "data/processed/topic_risk_analysis.csv"
)

fig = px.bar(
    risk_df,
    x="topic",
    y="risk_score",
    color="risk_level",
    text="risk_score"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.dataframe(
    risk_df,
    use_container_width=True
)