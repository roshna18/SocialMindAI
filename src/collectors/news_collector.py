from newsapi import NewsApiClient
import pandas as pd

# replace with your key
API_KEY = "f548dd2c0e3248f48c071610cbb415f0"

newsapi = NewsApiClient(api_key=API_KEY)

articles = newsapi.get_everything(
    q="Artificial Intelligence",
    language="en",
    sort_by="publishedAt",
    page_size=10
)

data = []

for article in articles["articles"]:

    data.append({
        "title": article["title"],
        "source": article["source"]["name"],
        "published": article["publishedAt"],
        "url": article["url"]
    })

df = pd.DataFrame(data)

print(df)

df.to_csv("data/news_data.csv", index=False)

print("\nNews data saved!")