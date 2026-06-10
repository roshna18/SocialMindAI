import streamlit as st

st.title("💡 Recommendations")

recommendations = {

    "Privacy": [
        "Increase transparency",
        "Improve communication",
        "Publish privacy updates"
    ],

    "Innovation": [
        "Promote successful AI projects",
        "Highlight achievements",
        "Showcase R&D initiatives"
    ],

    "AI Regulation": [
        "Publish governance reports",
        "Address compliance concerns",
        "Improve public trust"
    ],

    "Jobs": [
        "Improve workforce communication",
        "Share employee success stories",
        "Promote upskilling programs"
    ]
}

for topic, recs in recommendations.items():

    with st.expander(topic):

        for rec in recs:

            st.write(
                f"✅ {rec}"
            )