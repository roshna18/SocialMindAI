from transformers import pipeline

print("Loading model...")

classifier = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

print("Model loaded!\n")

result = classifier("I love artificial intelligence")

print(result)