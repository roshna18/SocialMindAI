import pandas as pd
import re

# ---------- TEXT CLEANING FUNCTION ----------

def clean_text(text):

    text = str(text).lower()

    # remove urls
    text = re.sub(r"http\S+", "", text)

    # remove special characters
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)

    # remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text

# ---------- CLEAN NEWS API DATA ----------

news_df = pd.read_csv("data/news_data.csv")

news_df.drop_duplicates(inplace=True)
news_df.dropna(inplace=True)

news_df["clean_title"] = news_df["title"].apply(clean_text)

news_df.to_csv("data/cleaned_news_data.csv", index=False)

print("News data cleaned!")

# ---------- CLEAN RSS DATA ----------

rss_df = pd.read_csv("data/rss_news.csv")

rss_df.drop_duplicates(inplace=True)
rss_df.dropna(inplace=True)

rss_df["clean_title"] = rss_df["title"].apply(clean_text)

rss_df.to_csv("data/cleaned_rss_data.csv", index=False)

print("RSS data cleaned!")

# ---------- CLEAN GOOGLE TRENDS DATA ----------

trends_df = pd.read_csv("data/google_trends.csv")

trends_df.drop_duplicates(inplace=True)
trends_df.dropna(inplace=True)

# convert date column
trends_df["date"] = pd.to_datetime(trends_df["date"])

trends_df.to_csv("data/cleaned_google_trends.csv", index=False)

print("Google Trends data cleaned!")

print("\nAll datasets cleaned successfully!")