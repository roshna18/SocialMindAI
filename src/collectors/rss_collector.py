import feedparser
import pandas as pd

# BBC Technology RSS Feed
url = "http://feeds.bbci.co.uk/news/technology/rss.xml"

feeds = [
    "http://feeds.bbci.co.uk/news/technology/rss.xml",
    "https://feeds.feedburner.com/TechCrunch",
    "https://www.theverge.com/rss/index.xml"
]

articles = []

for entry in feed.entries:

    articles.append({
        "title": entry.title,
        "published": entry.published,
        "link": entry.link
    })

df = pd.DataFrame(articles)

print(df.head())

df.to_csv("data/rss_news.csv", index=False)

print("\nRSS news data saved!")