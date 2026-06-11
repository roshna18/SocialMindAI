import pandas as pd

ISSUES = {

    "Stock Volatility": [
        "stock",
        "market",
        "shares",
        "investor",
        "ipo"
    ],

    "Product Quality": [
        "quality",
        "poorly built",
        "defect",
        "broken",
        "maintenance"
    ],

    "Brand Criticism": [
        "hate",
        "bad company",
        "ugly",
        "terrible"
    ],

    "Regulation": [
        "government",
        "regulation",
        "compliance"
    ]
}

# ==========================
# LOAD ANALYSIS
# ==========================

df = pd.read_csv(
    "data/live/reputation_analysis.csv"
)

negative_df = df[
    df["sentiment"] == "negative"
]

issue_counts = {}

# ==========================
# DETECT ISSUES
# ==========================

for issue, keywords in ISSUES.items():

    count = 0

    for text in negative_df["text"]:

        text = str(text).lower()

        for keyword in keywords:

            if keyword.lower() in text:

                count += 1
                break

    issue_counts[issue] = count

# ==========================
# RESULTS
# ==========================

issue_df = pd.DataFrame(
    list(issue_counts.items()),
    columns=[
        "issue",
        "count"
    ]
)

issue_df = issue_df.sort_values(
    by="count",
    ascending=False
)

print("\n" + "=" * 50)
print("DETECTED ISSUES")
print("=" * 50)

print(issue_df)

# ==========================
# TOP ISSUE
# ==========================

top_issue = issue_df.iloc[0]["issue"]

print(
    f"\nTop Issue: {top_issue}"
)

# ==========================
# SAVE
# ==========================

issue_df.to_csv(
    "data/live/issue_summary.csv",
    index=False
)

print(
    "\nSaved:"
)

print(
    "data/live/issue_summary.csv"
)