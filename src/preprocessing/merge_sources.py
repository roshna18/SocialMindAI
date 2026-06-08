import pandas as pd

# ---------------- LOAD RSS ----------------

rss = pd.read_csv("data/raw/rss_news.csv")

rss = rss.rename(columns={
    "title": "text",
    "link": "url"
})

rss["source_type"] = "RSS"
rss["data_category"] = "news"

rss = rss[[
    "text",
    "source_type",
    "data_category"
]]

# ---------------- LOAD GNEWS ----------------

gnews = pd.read_csv("data/raw/gnews_data.csv")

gnews = gnews.rename(columns={
    "title": "text"
})

gnews["source_type"] = "GNews"
gnews["data_category"] = "news"

gnews = gnews[[
    "text",
    "source_type",
    "data_category"
]]

# ---------------- LOAD YOUTUBE COMMENTS ----------------

youtube_df = pd.read_csv("data/raw/youtube_comments.csv")

youtube_df = youtube_df.rename(columns={
    "comment": "text"
})

youtube_df["source_type"] = "YouTube"
youtube_df["data_category"] = "social_comment"

youtube_df = youtube_df[[
    "text",
    "source_type",
    "data_category"
]]

# ---------------- MERGE ALL SOURCES ----------------

master_df = pd.concat(
    [rss, gnews, youtube_df],
    ignore_index=True
)

# remove duplicates
master_df.drop_duplicates(
    subset=["text"],
    inplace=True
)

# remove nulls
master_df.dropna(inplace=True)

# reset index
master_df.reset_index(drop=True, inplace=True)

# ---------------- OUTPUT ----------------

print(master_df.head())

print("\nDataset Shape:", master_df.shape)

print("\nSource Distribution:")
print(master_df["source_type"].value_counts())

# SAVE MASTER DATASET
master_df.to_csv(
    "data/processed/master_dataset.csv",
    index=False
)

print("\nMaster dataset created successfully!")