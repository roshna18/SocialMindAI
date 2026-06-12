import pandas as pd
from transformers import pipeline

TOPICS = [
    "Innovation",
    "Privacy",
    "AI Regulation",
    "Finance",
    "Jobs",
    "Education"
]

print("Loading models...")

# ==========================
# LOAD MODELS
# ==========================

sentiment_model = pipeline(
    "sentiment-analysis",
    model="ProsusAI/finbert"
)

topic_model = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

print("Models loaded.\n")

# ==========================
# LOAD DATA
# ==========================

df = pd.read_csv(
    "data/live/company_dataset.csv"
)

df["text"] = df["text"].astype(str)

print(f"Records loaded: {len(df)}")

# ==========================
# SENTIMENT ANALYSIS
# ==========================

print("\nRunning sentiment analysis...\n")

sentiments = []
scores = []

for i, text in enumerate(df["text"]):

    if i % 20 == 0:
        print(f"Sentiment: {i}/{len(df)}")

    try:

        result = sentiment_model(
            text[:512]
        )[0]

        sentiments.append(
            result["label"].lower()
        )

        scores.append(
            round(
                result["score"],
                4
            )
        )

    except Exception as e:

        print(
            f"Sentiment Error: {e}"
        )

        sentiments.append(
            "neutral"
        )

        scores.append(0)

df["sentiment"] = sentiments
df["confidence"] = scores

# ==========================
# POSITIVE / NEGATIVE
# ==========================

negative_mentions = (
    df[
        df["sentiment"] == "negative"
    ]["text"]
    .head(10)
    .tolist()
)

positive_mentions = (
    df[
        df["sentiment"] == "positive"
    ]["text"]
    .head(10)
    .tolist()
)

# ==========================
# TOPIC DETECTION
# ONLY NEWS
# ==========================

print("\nRunning topic detection...\n")

if "source" in df.columns:

    topic_df = df[
        df["source"] == "news"
    ].copy()

else:

    topic_df = df.copy()

topic_df = topic_df.head(
    min(20, len(topic_df))
)

topics = []

for i, text in enumerate(topic_df["text"]):

    if i % 5 == 0:
        print(
            f"Topics: {i}/{len(topic_df)}"
        )

    try:

        result = topic_model(
            text[:512],
            candidate_labels=TOPICS
        )

        topics.append(
            result["labels"][0]
        )

    except Exception as e:

        print(
            f"Topic Error: {e}"
        )

        topics.append(
            "Other"
        )

topic_df["topic"] = topics

# ==========================
# TOPIC SUMMARY
# ==========================

if len(topic_df) > 0:

    topic_summary = (
        topic_df["topic"]
        .value_counts()
    )

    top_topic = (
        topic_df["topic"]
        .value_counts()
        .idxmax()
    )

else:

    topic_summary = pd.Series()

    top_topic = "Unknown"

# ==========================
# METRICS
# ==========================

positive = len(
    df[
        df["sentiment"] == "positive"
    ]
)

negative = len(
    df[
        df["sentiment"] == "negative"
    ]
)

neutral = len(
    df[
        df["sentiment"] == "neutral"
    ]
)

total = len(df)

if (positive + negative) > 0:

    reputation_score = round(
        positive /
        (positive + negative)
        * 100,
        2
    )

else:

    reputation_score = 50

# ==========================
# GRADE
# ==========================

if reputation_score >= 80:
    grade = "Excellent"

elif reputation_score >= 65:
    grade = "Strong"

elif reputation_score >= 50:
    grade = "Mixed"

elif reputation_score >= 35:
    grade = "Weak"

else:
    grade = "Critical"

# ==========================
# RISK
# ==========================

if reputation_score >= 70:
    risk_level = "LOW"

elif reputation_score >= 40:
    risk_level = "MEDIUM"

else:
    risk_level = "HIGH"

# ==========================
# SOURCE SUMMARY
# ==========================

if "source" in df.columns:

    source_summary = pd.crosstab(
        df["source"],
        df["sentiment"]
    )

else:

    source_summary = "Source column unavailable"

# ==========================
# REPORT
# ==========================

print("\n" + "=" * 60)
print("SOCIALMIND AI REPUTATION REPORT")
print("=" * 60)

print(f"\nTotal Mentions: {total}")

print(f"Positive Mentions: {positive}")

print(f"Neutral Mentions: {neutral}")

print(f"Negative Mentions: {negative}")

print(
    f"\nPublic Sentiment Score: {reputation_score}/100"
)

print(
    f"Reputation Grade: {grade}"
)

print(
    f"Risk Level: {risk_level}"
)

print(
    f"\nMost Discussed Topic: {top_topic}"
)

print("\nTopic Distribution:")
print(topic_summary)

print("\nSource-wise Sentiment:")
print(source_summary)

print("\nTop Negative Mentions:")

for item in negative_mentions:
    print(f"- {item}")

print("\nTop Positive Mentions:")

for item in positive_mentions:
    print(f"- {item}")

# ==========================
# SAVE FILES
# ==========================

df.to_csv(
    "data/live/reputation_analysis.csv",
    index=False
)

summary = pd.DataFrame([{
    "reputation_score": reputation_score,
    "grade": grade,
    "risk_level": risk_level,
    "positive": positive,
    "neutral": neutral,
    "negative": negative,
    "top_topic": top_topic
}])

summary.to_csv(
    "data/live/reputation_summary.csv",
    index=False
)

print("\nSaved Files:")

print(
    "data/live/reputation_analysis.csv"
)

print(
    "data/live/reputation_summary.csv"
)