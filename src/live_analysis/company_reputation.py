import requests
import pandas as pd
from transformers import pipeline

# ==========================
# CONFIG
# ==========================

GNEWS_API_KEY = "70ee9796775424260d45f7ee5efd0071"

TOPICS = [
    "AI Regulation",
    "Innovation",
    "Privacy",
    "Finance",
    "Education",
    "Jobs"
]

# ==========================
# LOAD MODELS ONCE
# ==========================

print("Loading sentiment model...")

sentiment_model = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

print("Loading topic model...")

topic_model = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

print("Models loaded.\n")


# ==========================
# FETCH NEWS
# ==========================

def fetch_news(company):

    url = (
        f"https://gnews.io/api/v4/search?"
        f"q={company}"
        f"&lang=en"
        f"&max=20"
        f"&apikey={GNEWS_API_KEY}"
    )

    response = requests.get(url)

    data = response.json()

    articles = []

    for article in data.get("articles", []):

        articles.append({
            "title": article["title"],
            "description": article["description"],
            "source": article["source"]["name"],
            "published": article["publishedAt"]
        })

    return pd.DataFrame(articles)


# ==========================
# ANALYZE DATA
# ==========================

def analyze_company(company):

    print(f"\nFetching news for {company}...\n")

    df = fetch_news(company)

    if len(df) == 0:

        print("No articles found.")

        return

    sentiments = []
    confidence = []
    topics = []

    for title in df["title"]:

        # Sentiment
        s = sentiment_model(str(title))[0]

        sentiments.append(
            s["label"]
        )

        confidence.append(
            round(s["score"], 4)
        )

        # Topic
        t = topic_model(
            str(title),
            TOPICS
        )

        topics.append(
            t["labels"][0]
        )

    df["sentiment"] = sentiments
    df["confidence"] = confidence
    df["topic"] = topics

    # ======================
    # REPORT METRICS
    # ======================

    positive = len(
        df[df["sentiment"] == "POSITIVE"]
    )

    negative = len(
        df[df["sentiment"] == "NEGATIVE"]
    )

    total = len(df)

    brand_score = round(
        (positive / total) * 100,
        2
    )

    top_topic = (
        df["topic"]
        .value_counts()
        .idxmax()
    )

    # ======================
    # REPORT
    # ======================

    print("\n" + "=" * 60)
    print("SOCIALMIND AI COMPANY REPORT")
    print("=" * 60)

    print(f"\nCompany: {company}")

    print(f"\nTotal Mentions: {total}")

    print(f"Positive Mentions: {positive}")

    print(f"Negative Mentions: {negative}")

    print(f"Brand Score: {brand_score}/100")

    print(f"Top Discussion Topic: {top_topic}")

    print("\nSentiment Distribution:")

    print(
        df["sentiment"]
        .value_counts()
    )

    print("\nTopic Distribution:")

    print(
        df["topic"]
        .value_counts()
    )

    print("\nRecommended Actions:")

    if top_topic == "Privacy":

        print(
            "- Improve transparency"
        )

        print(
            "- Publish privacy updates"
        )

        print(
            "- Strengthen trust communication"
        )

    elif top_topic == "AI Regulation":

        print(
            "- Publish governance reports"
        )

        print(
            "- Highlight compliance efforts"
        )

    elif top_topic == "Innovation":

        print(
            "- Promote successful projects"
        )

        print(
            "- Highlight R&D achievements"
        )

    elif top_topic == "Finance":

        print(
            "- Improve investor communication"
        )

        print(
            "- Address market concerns"
        )

    elif top_topic == "Jobs":

        print(
            "- Highlight workforce growth"
        )

        print(
            "- Promote employee success stories"
        )

    elif top_topic == "Education":

        print(
            "- Expand learning resources"
        )

        print(
            "- Increase awareness initiatives"
        )

    # SAVE

    filename = (
        f"data/{company.lower()}_report.csv"
    )

    df.to_csv(
        filename,
        index=False
    )

    print(f"\nReport saved: {filename}")


# ==========================
# MAIN
# ==========================

if __name__ == "__main__":

    company = input(
        "Enter company name: "
    )

    analyze_company(company)