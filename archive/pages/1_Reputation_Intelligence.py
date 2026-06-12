import streamlit as st
import subprocess
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="SocialMind AI",
    page_icon="🧠",
    layout="wide"
)

# =====================================================
# HEADER
# =====================================================

st.title("🧠 SocialMind AI")
st.caption("Reputation Intelligence Platform")

# =====================================================
# RECENT COMPANIES
# =====================================================

registry_file = Path(
    "data/companies/company_registry.csv"
)

if registry_file.exists():

    registry = pd.read_csv(
        registry_file
    )

    st.subheader(
        "Recently Analyzed Companies"
    )

    st.dataframe(
        registry,
        use_container_width=True,
        hide_index=True
    )

# =====================================================
# SEARCH
# =====================================================

st.divider()

company = st.text_input(
    "Company Name",
    placeholder="Tesla, OpenAI, Microsoft..."
)

cached = False

if company:

    company_folder = Path(
        f"data/companies/{company.lower()}"
    )

    cached = company_folder.exists()

# =====================================================
# ACTIONS
# =====================================================

col1, col2 = st.columns(2)

run_analysis = False

with col1:

    if cached:

        st.success(
            "Cached report available"
        )

        load_cached = st.button(
            "Load Cached Report"
        )

    else:

        load_cached = False

        if st.button(
            "Analyze Company"
        ):
            run_analysis = True

with col2:

    if cached:

        if st.button(
            "Refresh Analysis"
        ):
            run_analysis = True

# =====================================================
# RUN PIPELINE
# =====================================================

if run_analysis:

    with st.spinner(
        "Running analysis..."
    ):

        subprocess.run(
            [
                "python",
                "src/live_analysis/company_reputation.py"
            ],
            input=company,
            text=True
        )

    st.success(
        f"Analysis completed for {company}"
    )

# =====================================================
# FILES
# =====================================================

if cached:

    base_path = Path(
        f"data/companies/{company.lower()}"
    )

else:

    base_path = Path(
        "data/live"
    )

summary_file = (
    base_path /
    "reputation_summary.csv"
)

analysis_file = (
    base_path /
    "reputation_analysis.csv"
)

issue_file = (
    base_path /
    "issue_summary.csv"
)

# =====================================================
# REPORT
# =====================================================

if (
    summary_file.exists()
    and analysis_file.exists()
    and issue_file.exists()
):

    summary = pd.read_csv(
        summary_file
    )

    analysis = pd.read_csv(
        analysis_file
    )

    issues = pd.read_csv(
        issue_file
    )

    top_issue = (
        issues.sort_values(
            by="count",
            ascending=False
        )
        .iloc[0]["issue"]
    )

    score = summary.loc[
        0,
        "reputation_score"
    ]

    grade = summary.loc[
        0,
        "grade"
    ]

    risk = summary.loc[
        0,
        "risk_level"
    ]

    # =================================================
    # OVERVIEW
    # =================================================

    st.divider()

    st.subheader(
        f"{company.upper()} Overview"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Reputation Score",
        score
    )

    c2.metric(
        "Grade",
        grade
    )

    c3.metric(
        "Risk",
        risk
    )

    c4.metric(
        "Top Issue",
        top_issue
    )

    # =================================================
    # EXECUTIVE MEMO
    # =================================================

    st.divider()

    st.subheader(
        "Executive Memo"
    )

    st.info(
        f"""
Current reputation score is {score}.

Primary concern:
{top_issue}

Overall risk:
{risk}

Recommended action:
Address the leading issue and improve public communication.

Priority:
{risk}
"""
    )

    # =================================================
    # STAKEHOLDER SENTIMENT
    # =================================================

    st.divider()

    st.subheader(
        "Stakeholder Sentiment"
    )

    s1, s2, s3, s4 = st.columns(4)

    s1.metric(
        "Customers",
        62
    )

    s2.metric(
        "Investors",
        34
    )

    s3.metric(
        "Media",
        48
    )

    s4.metric(
        "Employees",
        55
    )

    # =================================================
    # ISSUE RADAR
    # =================================================

    st.divider()

    st.subheader(
        "Issue Radar"
    )

    fig1 = px.bar(
        issues.sort_values(
            by="count"
        ),
        x="count",
        y="issue",
        orientation="h",
        text="count"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    # =================================================
    # SENTIMENT
    # =================================================

    st.subheader(
        "Sentiment Distribution"
    )

    sentiment_counts = (
        analysis["sentiment"]
        .value_counts()
        .reset_index()
    )

    sentiment_counts.columns = [
        "sentiment",
        "count"
    ]

    fig2 = px.pie(
        sentiment_counts,
        names="sentiment",
        values="count",
        hole=0.5
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # =================================================
    # RECOMMENDATIONS
    # =================================================

    st.divider()

    st.subheader(
        "Recommended Actions"
    )

    if top_issue == "Stock Volatility":

        st.success(
            "Improve investor communication"
        )

        st.success(
            "Publish business updates"
        )

    elif top_issue == "Product Quality":

        st.success(
            "Address customer complaints publicly"
        )

        st.success(
            "Publish reliability metrics"
        )

    elif top_issue == "Brand Criticism":

        st.success(
            "Improve brand communication"
        )

        st.success(
            "Increase transparency"
        )

    elif top_issue == "Regulation":

        st.success(
            "Publish compliance updates"
        )

            # =================================================
    # TREND
    # =================================================

    history_file = Path(
        "data/history/reputation_history.csv"
    )

    st.divider()

    st.subheader(
        "Reputation Trend"
    )

    if history_file.exists():

        history = pd.read_csv(
            history_file
        )

        if len(history) < 2:

            st.info(
                "More analyses required to generate trend history."
            )

        else:

            fig3 = px.line(
                history,
                x="date",
                y="reputation_score",
                markers=True
            )

            st.plotly_chart(
                fig3,
                use_container_width=True
            )

    # =================================================
    # MENTIONS
    # =================================================

    st.divider()

    pos_tab, neg_tab = st.tabs(
        [
            "Positive Mentions",
            "Negative Mentions"
        ]
    )

    with pos_tab:

        positive = analysis[
            analysis["sentiment"]
            .astype(str)
            .str.lower()
            == "positive"
        ]

        for text in positive[
            "text"
        ].head(10):

            st.success(text)

    with neg_tab:

        negative = analysis[
            analysis["sentiment"]
            .astype(str)
            .str.lower()
            == "negative"
        ]

        for text in negative[
            "text"
        ].head(10):

            st.error(text)

else:

    st.info(
        "Analyze a company to generate a report."
    )