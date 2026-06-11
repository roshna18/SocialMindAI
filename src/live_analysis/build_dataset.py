import pandas as pd

# NEWS

news_df = pd.read_csv(
    "data/live/news.csv"
)

news_df["source"] = "news"

news_df = news_df.rename(
    columns={
        "title": "text"
    }
)

news_df = news_df[
    ["source", "text"]
]

# YOUTUBE VIDEOS

videos_df = pd.read_csv(
    "data/live/youtube_videos.csv"
)

videos_df = videos_df[
    ["source", "text"]
]

# YOUTUBE COMMENTS

comments_df = pd.read_csv(
    "data/live/youtube_comments.csv"
)

comments_df = comments_df[
    ["source", "text"]
]

# MERGE

dataset = pd.concat(
    [
        news_df,
        videos_df,
        comments_df
    ],
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