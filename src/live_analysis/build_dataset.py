from pathlib import Path
import pandas as pd

frames = []

# ==========================
# SAFE CSV LOADER
# ==========================

def safe_read_csv(path):

    try:

        if not Path(path).exists():
            return None

        df = pd.read_csv(path)

        if len(df) == 0:
            return None

        return df

    except:

        return None


# ==========================
# NEWS
# ==========================

news_df = safe_read_csv(
    "data/live/news.csv"
)

if news_df is not None:

    news_df["source"] = "news"

    news_df = news_df.rename(
        columns={
            "title": "text"
        }
    )

    news_df = news_df[
        ["source", "text"]
    ]

    frames.append(news_df)

# ==========================
# YOUTUBE VIDEOS
# ==========================

videos_df = safe_read_csv(
    "data/live/youtube_videos.csv"
)

if videos_df is not None:

    videos_df = videos_df[
        ["source", "text"]
    ]

    frames.append(videos_df)

# ==========================
# YOUTUBE COMMENTS
# ==========================

comments_df = safe_read_csv(
    "data/live/youtube_comments.csv"
)

if comments_df is not None:

    comments_df = comments_df[
        ["source", "text"]
    ]

    frames.append(comments_df)

# ==========================
# NO DATA
# ==========================

if len(frames) == 0:

    print(
        "\nNo data collected."
    )

    exit()

# ==========================
# MERGE
# ==========================

dataset = pd.concat(
    frames,
    ignore_index=True
)

dataset.drop_duplicates(
    subset=["text"],
    inplace=True
)

dataset.to_csv(
    "data/live/company_dataset.csv",
    index=False
)

print(
    f"\nDataset Size: {len(dataset)}"
)

print(
    "\nDataset created successfully."
)