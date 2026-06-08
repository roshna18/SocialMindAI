import requests
import pandas as pd

API_KEY = "70ee9796775424260d45f7ee5efd0071"

topics = [
    "Artificial Intelligence",
    "ChatGPT",
    "OpenAI",
    "Machine Learning"
]

articles = []

for topic in topics:

    print(f"Fetching {topic}...")

    url = (
        f"https://gnews.io/api/v4/search?"
        f"q={topic}&lang=en&max=10&apikey={API_KEY}"
    )

    response = requests.get(url)
    data = response.json()

    for article in data.get("articles", []):

        articles.append({
            "topic": topic,
            "title": article["title"],
            "source": article["source"]["name"],
            "published": article["publishedAt"],
            "url": article["url"]
        })

df = pd.DataFrame(articles)

df.drop_duplicates(subset=["title"], inplace=True)

print("\nTotal Articles:", len(df))

df.to_csv("data/gnews_data.csv", index=False)

print("GNews data saved!")