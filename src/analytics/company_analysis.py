import pandas as pd

df = pd.read_csv(
    "data/processed/final_analyzed_data.csv"
)

companies = [
    "openai",
    "google",
    "meta",
    "microsoft",
    "anthropic",
    "nvidia"
]

results = []

for company in companies:

    company_df = df[
        df["cleaned_text"].str.contains(
            company,
            case=False,
            na=False
        )
    ]

    if len(company_df) == 0:
        continue

    total = len(company_df)

    positive = len(
        company_df[
            company_df["sentiment"] == "POSITIVE"
        ]
    )

    negative = len(
        company_df[
            company_df["sentiment"] == "NEGATIVE"
        ]
    )

    results.append({
        "company": company,
        "mentions": total,
        "positive": positive,
        "negative": negative
    })

result_df = pd.DataFrame(results)

print(result_df)

result_df.to_csv(
    "data/processed/company_analysis.csv",
    index=False
)