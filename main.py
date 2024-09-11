from fastapi import FastAPI, Query, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import httpx
from cachetools import TTLCache
from datetime import datetime, timedelta

app = FastAPI()

# Create a cache with a 10-minute expiration
cache = TTLCache(maxsize=100, ttl=600)

# Hacker News API URLs
HN_API_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"

# Existing Hello World route
@app.get("/")
def read_root():
    return {"Hello": "World"}

# New route to fetch top stories from Hacker News with caching
@app.get("/top-news")
async def get_top_news(count: int = Query(10, gt=0)):
    try:
        # Check if the result is cached
        if count in cache:
            return cache[count]

        # Fetch top story IDs
        async with httpx.AsyncClient() as client:
            response = await client.get(HN_API_URL)
            response.raise_for_status()
            top_story_ids = response.json()[:count]

            # Fetch details for each story
            top_stories = []
            for story_id in top_story_ids:
                story_response = await client.get(HN_ITEM_URL.format(story_id))
                story_response.raise_for_status()
                top_stories.append(story_response.json())

            # Store the result in cache
            cache[count] = top_stories
            return top_stories

    except httpx.HTTPStatusError as http_err:
        raise HTTPException(status_code=http_err.response.status_code, detail=str(http_err))
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))

# Example Pydantic model for response (optional, if needed)
class NewsItem(BaseModel):
    by: str
    id: int
    kids: Optional[list[int]]
    parent: Optional[int]
    parts: Optional[list[int]]
    score: int
    text: Optional[str]
    time: int
    title: str
    type: str
    url: Optional[str]

    class Config:
        from_attributes = True

# Configure OAuth2 for Salesforce (optional and requires correct setup)
from fastapi.security import OAuth2AuthorizationCodeBearer

# Standard OAuth2 configuration
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://login.salesforce.com/services/oauth2/authorize",
    tokenUrl="https://login.salesforce.com/services/oauth2/token"
)

@app.get("/secure-top-news")
async def secure_top_news(token: str = Depends(oauth2_scheme)):
    # Validate the token and then call the existing /top-news endpoint or functionality
    return await get_top_news()  # Example of calling the existing endpoint

# Add this part to run the app with Uvicorn when the script is executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
