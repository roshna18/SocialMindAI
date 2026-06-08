
from googleapiclient.discovery import build
import pandas as pd

API_KEY = "AIzaSyA7rF3n6D24zICDBH80sYfiEyhyMFDo82M"

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)

search_query = "Artificial Intelligence"

# SEARCH VIDEOS
request = youtube.search().list(
    q=search_query,
    part="snippet",
    maxResults=5,
    type="video"
)

response = request.execute()

videos = []
comments_data = []

for item in response["items"]:

    video_id = item["id"]["videoId"]

    title = item["snippet"]["title"]

    videos.append({
        "video_id": video_id,
        "title": title,
        "channel": item["snippet"]["channelTitle"],
        "published": item["snippet"]["publishedAt"]
    })

    print(f"\nFetching comments for: {title}")

    try:

        comment_request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=20,
            textFormat="plainText"
        )

        comment_response = comment_request.execute()

        for comment in comment_response["items"]:

            text = comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"]

            likes = comment["snippet"]["topLevelComment"]["snippet"]["likeCount"]

            comments_data.append({
                "video_title": title,
                "comment": text,
                "likes": likes
            })

    except Exception as e:
        print("Comments disabled or unavailable")

# SAVE VIDEOS
videos_df = pd.DataFrame(videos)

videos_df.to_csv("data/youtube_videos.csv", index=False)

# SAVE COMMENTS
comments_df = pd.DataFrame(comments_data)

comments_df.to_csv("data/youtube_comments.csv", index=False)

print("\nYouTube comments saved!")

print(f"\nTotal Comments Collected: {len(comments_df)}")