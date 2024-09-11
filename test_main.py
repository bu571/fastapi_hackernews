from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Test for Hello World route
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

# Test for Hacker News top stories route
def test_get_top_stories():
    response = client.get("/hackernews/topstories")
    assert response.status_code == 200
    # Check if "top_stories" is in the response JSON
    assert "top_stories" in response.json()
