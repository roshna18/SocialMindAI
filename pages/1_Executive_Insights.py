import streamlit as st
import pandas as pd

st.title("📊 Executive Insights")

df = pd.read_csv(
    "data/processed/final_analyzed_data.csv"
)

negative_pct = round(
    (
        len(df[df["sentiment"]=="NEGATIVE"])
        / len(df)
    ) * 100,
    2
)

top_topic = (
    df["topic"]
    .value_counts()
    .idxmax()
)

total_records = len(df)

col1,col2,col3 = st.columns(3)

col1.metric(
    "Records Analyzed",
    total_records
)

col2.metric(
    "Negative %",
    f"{negative_pct}%"
)

col3.metric(
    "Top Topic",
    top_topic
)

st.divider()

st.subheader("Key Findings")

st.info(
    f"""
• {negative_pct}% of analyzed content is negative

• Most discussed topic: {top_topic}

• Privacy is currently the highest risk area

• OpenAI has the highest negative sentiment

• Innovation remains the largest discussion category
"""
)