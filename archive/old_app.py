import streamlit as st

st.set_page_config(
    page_title="SocialMind AI",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 SocialMind AI")

st.subheader(
    "Reputation Intelligence Platform"
)

st.markdown(
"""
Monitor public perception,
detect emerging risks,
analyze sentiment,
and generate executive recommendations.
"""
)

col1,col2,col3 = st.columns(3)

with col1:
    st.metric(
        "Sources",
        "News + YouTube"
    )

with col2:
    st.metric(
        "AI Models",
        "FinBERT + BART"
    )

with col3:
    st.metric(
        "Capabilities",
        "5"
    )

st.divider()

st.markdown("""
### Platform Modules

- Executive Overview
- Risk Intelligence
- Company Intelligence
- Reputation Analysis
- Data Explorer

### Coming Soon

- Crisis Radar
- Stakeholder Intelligence
- Competitor Benchmarking
- Executive Memo
- Reputation Timeline
""")