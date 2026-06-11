import pandas as pd

history = pd.read_csv(
    "data/history/reputation_history.csv"
)

company = input(
    "Company Name: "
)

company_df = history[
    history["company"]
    .str.lower()
    ==
    company.lower()
]

print("\nTrend History:\n")

print(
    company_df[
        [
            "date",
            "reputation_score",
            "grade"
        ]
    ]
)