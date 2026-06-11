from googleapiclient.discovery import build
import pandas as pd

API_KEY = "AIzaSyA7rF3n6D24zICDBH80sYfiEyhyMFDo82M"

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)

def fetch_youtube(company):

    print(f"\nSearching YouTube for {company}...\n")

    request = youtube.search().list(
        q=company,
        part="snippet",
        maxResults=10,
        type="video"
    )

    response = request.execute()

    videos = []
    comments = []

    for item in response["items"]:

        video_id = item["id"]["videoId"]

        title = item["snippet"]["title"]

        description = item["snippet"]["description"]

        videos.append({
            "source": "youtube_video",
            "text": title,
            "video_id": video_id
        })

        try:

            comment_request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=20,
                textFormat="plainText"
            )

            comment_response = comment_request.execute()

            for comment in comment_response["items"]:

                comment_text = (
                    comment["snippet"]
                    ["topLevelComment"]
                    ["snippet"]
                    ["textDisplay"]
                )

                comments.append({
                    "source": "youtube_comment",
                    "text": comment_text,
                    "video_id": video_id
                })

        except:
            pass

    videos_df = pd.DataFrame(videos)

    comments_df = pd.DataFrame(comments)

    return videos_df, comments_df


if __name__ == "__main__":

    company = input(
        "Enter company name: "
    )

    videos_df, comments_df = fetch_youtube(
        company
    )

    videos_df.to_csv(
        "data/live/youtube_videos.csv",
        index=False
    )

    comments_df.to_csv(
        "data/live/youtube_comments.csv",
        index=False
    )

    print(
        f"\nVideos: {len(videos_df)}"
    )

    print(
        f"Comments: {len(comments_df)}"
    )