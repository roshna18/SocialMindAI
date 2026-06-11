import subprocess

print("=" * 60)
print("SOCIALMIND AI")
print("COMPANY REPUTATION ANALYZER")
print("=" * 60)

company = input(
    "\nEnter Company Name: "
)

# ==========================
# NEWS
# ==========================

print("\n[1/5] Fetching News...\n")

subprocess.run(
    [
        "python",
        "src/live_analysis/fetch_company_news.py"
    ],
    input=company,
    text=True
)

# ==========================
# YOUTUBE
# ==========================

print("\n[2/5] Fetching YouTube...\n")

subprocess.run(
    [
        "python",
        "src/live_analysis/fetch_youtube.py"
    ],
    input=company,
    text=True
)

# ==========================
# DATASET
# ==========================

print("\n[3/5] Building Dataset...\n")

subprocess.run(
    [
        "python",
        "src/live_analysis/build_dataset.py"
    ]
)

# ==========================
# REPUTATION
# ==========================

print("\n[4/5] Running Reputation Analysis...\n")

subprocess.run(
    [
        "python",
        "src/live_analysis/reputation_engine.py"
    ]
)

# ==========================
# ADVISOR
# ==========================

print("\n[5/5] Generating Advisory Report...\n")

subprocess.run(
    [
        "python",
        "src/analytics/issue_extractor.py"
    ]
)

subprocess.run(
    [
        "python",
        "src/analytics/company_advisor.py"
    ]
)

print("\nDone.")