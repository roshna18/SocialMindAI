import pandas as pd
from datetime import datetime
from pathlib import Path

summary = pd.read_csv(
    "data/live/reputation_summary.csv"
)

company = input(
    "Company Name: "
)

summary["company"] = company
summary["date"] = datetime.now().date()

history_file = (
    "data/history/reputation_history.csv"
)

if Path(history_file).exists():

    old = pd.read_csv(
        history_file
    )

    summary = pd.concat(
        [old, summary],
        ignore_index=True
    )

summary.to_csv(
    history_file,
    index=False
)

print(
    "\nHistory Updated"
)