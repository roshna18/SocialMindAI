import pandas as pd

df = pd.read_csv(
    "data/processed/final_analyzed_data.csv"
)

summary = pd.crosstab(
    df["topic"],
    df["sentiment"]
)

print(summary)

summary.to_csv(
    "data/processed/topic_sentiment_summary.csv"
)

print("\nTopic sentiment summary saved!")