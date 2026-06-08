import pandas as pd

risk_df = pd.read_csv(
    "data/processed/topic_risk_analysis.csv"
)

recommendations = {

    "AI Regulation": [
        "Publish compliance and governance updates",
        "Improve transparency around AI usage",
        "Address regulatory concerns proactively"
    ],

    "Jobs": [
        "Communicate hiring and workforce strategy",
        "Highlight employee success stories",
        "Invest in employee upskilling initiatives"
    ],

    "Innovation": [
        "Promote successful AI initiatives",
        "Showcase product improvements",
        "Increase visibility of R&D achievements"
    ],

    "Privacy": [
        "Maintain strong privacy communication",
        "Continue transparency efforts",
        "Publish security and privacy updates"
    ],

    "Education": [
        "Expand educational resources",
        "Create training programs",
        "Increase awareness initiatives"
    ],

    "Other": [
        "Monitor emerging discussions",
        "Track sentiment trends",
        "Investigate recurring concerns"
    ]
}

print("\nEXECUTIVE ADVISORY REPORT\n")

for _, row in risk_df.iterrows():

    topic = row["topic"]

    print("=" * 60)

    print(f"TOPIC: {topic}")

    print(f"RISK LEVEL: {row['risk_level']}")

    print(f"RISK SCORE: {row['risk_score']}%")

    print("\nRecommended Actions:")

    for rec in recommendations.get(topic, []):

        print(f"✓ {rec}")

    print()