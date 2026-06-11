import streamlit as st
import subprocess
import pandas as pd

st.title(
    "🏢 Company Reputation Analyzer"
)

company = st.text_input(
    "Enter Company Name"
)

if st.button(
    "Analyze"
):

    subprocess.run(
        [
            "python",
            "src/live_analysis/company_reputation.py"
        ],
        input=company,
        text=True
    )

    summary = pd.read_csv(
        "data/live/reputation_summary.csv"
    )

    st.metric(
        "Public Sentiment Score",
        summary.loc[
            0,
            "reputation_score"
        ]
    )

    st.metric(
        "Grade",
        summary.loc[
            0,
            "grade"
        ]
    )

    st.metric(
        "Risk Level",
        summary.loc[
            0,
            "risk_level"
        ]
    )

    issues = pd.read_csv(
        "data/live/issue_summary.csv"
    )

    st.subheader(
        "Detected Issues"
    )

    st.dataframe(
        issues
    )