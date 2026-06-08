import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="SocialMind AI",
    layout="wide"
)

# ---------------- LOAD DATA ----------------

df = pd.read_csv(
    "data/processed/unified_sentiment.csv"
)

trends_df = pd.read_csv(
    "data/raw/google_trends.csv"
)

# ---------------- TITLE ----------------

st.title("🧠 SocialMind AI")

st.markdown(
    "AI-Powered Multi-Source Sentiment Intelligence Dashboard"
)

# ---------------- KPI SECTION ----------------

total_records = len(df)

positive_count = len(
    df[df["sentiment"] == "POSITIVE"]
)

negative_count = len(
    df[df["sentiment"] == "NEGATIVE"]
)

avg_confidence = round(
    df["confidence_score"].mean(),
    2
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Records",
    total_records
)

col2.metric(
    "Positive",
    positive_count
)

col3.metric(
    "Negative",
    negative_count
)

col4.metric(
    "Avg Confidence",
    avg_confidence
)

st.divider()

# ---------------- SOURCE DISTRIBUTION ----------------

col1, col2 = st.columns(2)

with col1:

    st.subheader("Source Distribution")

    source_counts = (
        df["source_type"]
        .value_counts()
        .reset_index()
    )

    fig1 = px.pie(
        source_counts,
        names="source_type",
        values="count"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

# ---------------- SENTIMENT DISTRIBUTION ----------------

with col2:

    st.subheader("Sentiment Distribution")

    sentiment_counts = (
        df["sentiment"]
        .value_counts()
        .reset_index()
    )

    fig2 = px.bar(
        sentiment_counts,
        x="sentiment",
        y="count"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

st.divider()

# ---------------- SOURCE-WISE SENTIMENT ----------------

st.subheader("Source-wise Sentiment Analysis")

cross_tab = pd.crosstab(
    df["source_type"],
    df["sentiment"]
)

fig3 = px.bar(
    cross_tab,
    barmode="group"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

st.divider()

# ---------------- CONFIDENCE DISTRIBUTION ----------------

st.subheader("Transformer Confidence Scores")

fig4 = px.histogram(
    df,
    x="confidence_score",
    nbins=20
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

st.divider()

# ---------------- GOOGLE TRENDS ----------------

st.subheader("Google Trends")

trends_df["date"] = pd.to_datetime(
    trends_df["date"]
)

trend_column = trends_df.columns[1]

fig5 = px.line(
    trends_df,
    x="date",
    y=trend_column
)

st.plotly_chart(
    fig5,
    use_container_width=True
)

st.divider()

# ---------------- DATA EXPLORER ----------------

st.subheader("Explore Data")

selected_source = st.selectbox(
    "Filter by Source",
    ["All"] + list(df["source_type"].unique())
)

filtered_df = df.copy()

if selected_source != "All":

    filtered_df = filtered_df[
        filtered_df["source_type"] == selected_source
    ]

st.dataframe(
    filtered_df[
        [
            "text",
            "source_type",
            "sentiment",
            "confidence_score"
        ]
    ],
    use_container_width=True
)