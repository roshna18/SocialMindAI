from pathlib import Path
import shutil
import pandas as pd

BASE_PATH = Path(
    "data/companies"
)

BASE_PATH.mkdir(
    parents=True,
    exist_ok=True
)


def company_folder(company):

    return BASE_PATH / company.lower()


def company_exists(company):

    return company_folder(
        company
    ).exists()


def save_company(company):

    folder = company_folder(
        company
    )

    folder.mkdir(
        parents=True,
        exist_ok=True
    )

    files = [

        "reputation_summary.csv",

        "reputation_analysis.csv",

        "issue_summary.csv",

        "company_dataset.csv"

    ]

    for file in files:

        source = Path(
            f"data/live/{file}"
        )

        if source.exists():

            shutil.copy(
                source,
                folder / file
            )

    update_registry(company)


def update_registry(company):

    registry_file = Path(
        "data/companies/company_registry.csv"
    )

    summary_file = (
        company_folder(company)
        /
        "reputation_summary.csv"
    )

    if not summary_file.exists():
        return

    summary = pd.read_csv(
        summary_file
    )

    row = {

        "company": company,

        "score":
        summary.loc[
            0,
            "reputation_score"
        ],

        "grade":
        summary.loc[
            0,
            "grade"
        ],

        "risk":
        summary.loc[
            0,
            "risk_level"
        ]
    }

    if registry_file.exists():

        registry = pd.read_csv(
            registry_file
        )

        registry = registry[
            registry["company"]
            .str.lower()
            != company.lower()
        ]

    else:

        registry = pd.DataFrame()

    registry = pd.concat(
        [
            registry,
            pd.DataFrame([row])
        ],
        ignore_index=True
    )

    registry.to_csv(
        registry_file,
        index=False
    )


def load_company(company):

    folder = company_folder(
        company
    )

    return {

        "summary":
        folder /
        "reputation_summary.csv",

        "analysis":
        folder /
        "reputation_analysis.csv",

        "issues":
        folder /
        "issue_summary.csv",

        "dataset":
        folder /
        "company_dataset.csv"
    }