from fastapi import FastAPI, HTTPException, Query
import requests
from cachetools import TTLCache

app = FastAPI()

# Create a cache with a 10-minute expiration
cache = TTLCache(maxsize=100, ttl=600)

HN_API_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"

@app.get("/top-news")
async def get_top_news(count: int = Query(10, gt=0)):
    try:
        # Check if the result is cached
        if count in cache:
            return cache[count]

        # Fetch top story IDs
        response = requests.get(HN_API_URL)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Hacker News API error")

        top_story_ids = response.json()[:count]

        # Fetch details for each story
        top_stories = []
        for story_id in top_story_ids:
            story_response = requests.get(HN_ITEM_URL.format(story_id))
            if story_response.status_code == 200:
                top_stories.append(story_response.json())

        # Store the result in cache
        cache[count] = top_stories
        return top_stories

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
