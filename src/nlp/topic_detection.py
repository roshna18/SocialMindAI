import pandas as pd

df = pd.read_csv("data/processed/unified_sentiment.csv")

TOPICS = {

    "AI Regulation": [
        "regulation","policy","government","law",
        "ban","compliance","legal","court","rules"
    ],

    "Jobs": [
        "job","jobs","employee","worker",
        "hiring","career","layoff","salary",
        "recruitment","staff"
    ],

    "Innovation": [
        "research","technology","innovation",
        "breakthrough","model","ai","artificial intelligence",
        "machine learning","openai","chatgpt"
    ],

    "Finance": [
        "stock","market","profit",
        "revenue","investment","earnings",
        "shares","financial"
    ],

    "Education": [
        "student","course","training",
        "learn","education","school",
        "university"
    ],

    "Privacy": [
        "privacy","tracking","data",
        "security","surveillance",
        "personal information"
    ],

    "Business": [
        "company","business",
        "enterprise","industry",
        "startup","organization"
    ]
}

def detect_topic(text):

    text = str(text).lower()

    for topic, keywords in TOPICS.items():

        if any(word in text for word in keywords):
            return topic

    return "Other"

df["topic"] = df["cleaned_text"].apply(detect_topic)

print(df["topic"].value_counts())

df.to_csv(
    "data/processed/final_analyzed_data.csv",
    index=False
)

print("Topics generated successfully!")