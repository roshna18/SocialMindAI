import streamlit as st
import pandas as pd

st.title("🏢 Company Reputation Analyzer")

company = st.text_input(
    "Enter Company Name",
    ""
)

if company:

    df = pd.read_csv(
        "data/processed/final_analyzed_data.csv"
    )

    company_rows = df[
        df["text"]
        .str.contains(
            company,
            case=False,
            na=False
        )
    ]

    if len(company_rows) == 0:

        st.warning(
            "No mentions found."
        )

    else:

        total = len(company_rows)

        positive = len(
            company_rows[
                company_rows["sentiment"]=="POSITIVE"
            ]
        )

        negative = len(
            company_rows[
                company_rows["sentiment"]=="NEGATIVE"
            ]
        )

        sentiment_score = round(
            (positive / total) * 100,
            2
        )

        st.metric(
            "Public Perception Score",
            f"{sentiment_score}"
        )

        st.metric(
            "Mentions",
            total
        )

        st.metric(
            "Negative Mentions",
            negative
        )

        st.dataframe(
            company_rows[
                [
                    "text",
                    "sentiment",
                    "topic"
                ]
            ]
        )