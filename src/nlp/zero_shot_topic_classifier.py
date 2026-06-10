from transformers import pipeline
import pandas as pd

print("Loading BART model...")

classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

print("Model loaded!")

df = pd.read_csv(
    "data/processed/unified_sentiment.csv"
)

candidate_labels = [
    "AI Regulation",
    "Innovation",
    "Jobs",
    "Privacy",
    "Education",
    "Finance"
]

topics = []

for text in df["cleaned_text"]:

    result = classifier(
        str(text),
        candidate_labels
    )

    topics.append(
        result["labels"][0]
    )

df["topic"] = topics

print(
    df["topic"].value_counts()
)

df.to_csv(
    "data/processed/final_analyzed_data.csv",
    index=False
)

print("\nTransformer topic classification completed!")