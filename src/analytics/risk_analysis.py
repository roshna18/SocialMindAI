import pandas as pd

df = pd.read_csv(
    "data/processed/final_analyzed_data.csv"
)

results = []

for topic in df["topic"].unique():

    topic_df = df[df["topic"] == topic]

    total = len(topic_df)

    negative = len(
        topic_df[topic_df["sentiment"] == "NEGATIVE"]
    )

    positive = len(
        topic_df[topic_df["sentiment"] == "POSITIVE"]
    )

    volume_weight = min(total / 10, 1)

    risk_score = round(
    ((negative / total) * 100)
    * volume_weight,
    2
)

    if risk_score >= 70:
        risk_level = "HIGH"

    elif risk_score >= 40:
        risk_level = "MEDIUM"

    else:
        risk_level = "LOW"

    results.append({
        "topic": topic,
        "total_mentions": total,
        "positive": positive,
        "negative": negative,
        "risk_score": risk_score,
        "risk_level": risk_level
    })

risk_df = pd.DataFrame(results)

risk_df = risk_df.sort_values(
    by="risk_score",
    ascending=False
)

print(risk_df)

risk_df.to_csv(
    "data/processed/topic_risk_analysis.csv",
    index=False
)

print("\nRisk analysis completed!")