import pandas as pd

summary = pd.read_csv(
    "data/live/reputation_summary.csv"
)

issues = pd.read_csv(
    "data/live/issue_summary.csv"
)

score = summary.loc[0, "reputation_score"]
grade = summary.loc[0, "grade"]

print("\n" + "=" * 60)
print("COMPANY ADVISORY REPORT")
print("=" * 60)

print(f"\nPublic Sentiment Score: {score}")
print(f"Reputation Grade: {grade}")

print("\nDetected Issues:")

for _, row in issues.iterrows():

    if row["count"] > 0:

        print(
            f"- {row['issue']} ({row['count']})"
        )

print("\nRecommended Actions:")

for _, row in issues.iterrows():

    issue = row["issue"]

    if row["count"] == 0:
        continue

    if issue == "Brand Criticism":

        print(
            "✓ Improve brand communication"
        )

        print(
            "✓ Highlight customer success stories"
        )

    elif issue == "Stock Volatility":

        print(
            "✓ Improve investor communication"
        )

        print(
            "✓ Publish business performance updates"
        )

    elif issue == "Product Quality":

        print(
            "✓ Publish reliability metrics"
        )

        print(
            "✓ Address product complaints publicly"
        )

    elif issue == "Regulation":

        print(
            "✓ Increase transparency"
        )

        print(
            "✓ Publish compliance updates"
        )

print("\nPriority Level:")

if score < 40:
    print("HIGH")

elif score < 65:
    print("MEDIUM")

else:
    print("LOW")