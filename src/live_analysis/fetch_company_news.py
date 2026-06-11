import requests
import pandas as pd

API_KEY = "70ee9796775424260d45f7ee5efd0071"

def fetch_company_news(company):

    url = (
        f"https://gnews.io/api/v4/search?"
        f"q={company}"
        f"&lang=en"
        f"&max=20"
        f"&apikey={API_KEY}"
    )

    response = requests.get(url)

    data = response.json()

    articles = []

    for article in data.get("articles", []):

        articles.append({
            "title": article["title"],
            "description": article["description"],
            "published": article["publishedAt"],
            "source": article["source"]["name"]
        })

    return pd.DataFrame(articles)


if __name__ == "__main__":

    company = input("Enter company name: ")

    df = fetch_company_news(company)

    print(df.head())

    df.to_csv(
        "data/live/news.csv",
        index=False
    )

    print("\nNews saved.")