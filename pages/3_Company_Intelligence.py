import streamlit as st
import pandas as pd
import plotly.express as px

st.title("🏢 Company Intelligence")

df = pd.read_csv(
    "data/processed/company_analysis.csv"
)

most_risky = (
    df.sort_values(
        by="negative",
        ascending=False
    )
    .iloc[0]["company"]
)

st.metric(
    "Most At-Risk Company",
    most_risky.upper()
)

fig = px.bar(
    df,
    x="company",
    y=["positive","negative"],
    barmode="group"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.dataframe(
    df,
    use_container_width=True
)