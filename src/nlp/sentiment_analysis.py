from textblob import TextBlob
import pandas as pd

# LOAD CLEANED DATA
df = pd.read_csv("data/cleaned_news_data.csv")

results = []

# POSITIVE & NEGATIVE KEYWORDS
positive_keywords = [
    "growth",
    "success",
    "launch",
    "improve",
    "rise",
    "innovation",
    "award",
    "profit",
    "boost",
    "expansion",
    "hiring",
    "climbs",
    "increase",
    "gains",
    "record",
    "opportunity",
    "partnership",
    "advancement"
]

negative_keywords = [
    "loss",
    "decline",
    "fear",
    "layoff",
    "crash",
    "drop",
    "risk",
    "ban",
    "lawsuit",
    "failure",
    "ordered",
    "warning",
    "concern",
    "fall",
    "investigation",
    "fine",
    "problem"
]

print("Running sentiment analysis...\n")

for text in df["clean_title"]:

    analysis = TextBlob(text)

    polarity = analysis.sentiment.polarity

    text_lower = text.lower()

    # HYBRID SENTIMENT LOGIC
    if any(word in text_lower for word in positive_keywords):
        sentiment = "POSITIVE"

    elif any(word in text_lower for word in negative_keywords):
        sentiment = "NEGATIVE"

    else:
        if polarity > 0:
            sentiment = "POSITIVE"

        elif polarity < 0:
            sentiment = "NEGATIVE"

        else:
            sentiment = "NEUTRAL"

    results.append({
        "text": text,
        "polarity": polarity,
        "sentiment": sentiment
    })

# CREATE DATAFRAME
result_df = pd.DataFrame(results)

print(result_df.head())

# SAVE RESULTS
result_df.to_csv("data/sentiment_results.csv", index=False)

print("\nImproved sentiment analysis completed!")