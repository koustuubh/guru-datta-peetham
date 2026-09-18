import os
import sys
import json

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import youtube_service

def sync():
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "data"))
    os.makedirs(data_dir, exist_ok=True)

    print("Fetching live YouTube video & shorts feed for @Rushivani...")
    feed_data = youtube_service.fetch_rushivani_feed()
    feed_file = os.path.join(data_dir, "youtube_feed.json")
    with open(feed_file, "w", encoding="utf-8") as f:
        json.dump(feed_data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(feed_data.get('shorts', []))} shorts and {len(feed_data.get('videos', []))} videos to {feed_file}")

    print("Fetching live YouTube community posts for @Rushivani...")
    posts_data = youtube_service.fetch_rushivani_posts()
    posts_file = os.path.join(data_dir, "youtube_posts.json")
    with open(posts_file, "w", encoding="utf-8") as f:
        json.dump(posts_data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(posts_data.get('posts', []))} community posts to {posts_file}")

if __name__ == "__main__":
    sync()
