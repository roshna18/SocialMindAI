from pytrends.request import TrendReq
import pandas as pd

print("Connecting to Google Trends...")

pytrends = TrendReq(hl='en-US', tz=360)

keywords = [
    "Artificial Intelligence",
    "ChatGPT",
    "OpenAI",
    "Machine Learning"
]

print("Building payload...")

pytrends.build_payload(
    keywords,
    timeframe='today 12-m'
)

print("Fetching data...")

data = pytrends.interest_over_time()

print("\nRAW DATA:")
print(data)

if not data.empty:

    if 'isPartial' in data.columns:
        data = data.drop(columns=['isPartial'])

    data.to_csv("data/google_trends.csv")

    print("\nGoogle Trends data saved!")

else:
    print("\nNo data returned.")