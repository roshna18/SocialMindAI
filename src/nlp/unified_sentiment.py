from transformers import pipeline
import pandas as pd
import re

print("Loading transformer model...\n")

# LOAD MODEL
classifier = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

print("Model loaded successfully!\n")

# LOAD MASTER DATASET
df = pd.read_csv("data/processed/master_dataset.csv")

# CLEAN FUNCTION
def clean_text(text):

    text = str(text).lower()

    text = re.sub(r"http\S+", "", text)

    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)

    text = re.sub(r"\s+", " ", text).strip()

    return text

results = []

print("Running transformer sentiment analysis...\n")

for _, row in df.iterrows():

    original_text = row["text"]

    cleaned_text = clean_text(original_text)

    # TRANSFORMER PREDICTION
    prediction = classifier(cleaned_text)[0]

    sentiment = prediction["label"]

    score = prediction["score"]

    results.append({
        "text": original_text,
        "cleaned_text": cleaned_text,
        "source_type": row["source_type"],
        "data_category": row["data_category"],
        "sentiment": sentiment,
        "confidence_score": score
    })

# CREATE DATAFRAME
result_df = pd.DataFrame(results)

# OUTPUTS
print(result_df.head())

print("\nOverall Sentiment Distribution:")
print(result_df["sentiment"].value_counts())

print("\nSource-wise Sentiment:")
print(
    pd.crosstab(
        result_df["source_type"],
        result_df["sentiment"]
    )
)

# SAVE RESULTS
result_df.to_csv(
    "data/processed/unified_sentiment.csv",
    index=False
)

print(f"\nProcessed {len(result_df)} records.")

print("\nTransformer sentiment analysis completed!")