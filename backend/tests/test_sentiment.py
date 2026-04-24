import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_sentiment_positive():
    """Positive review text should return positive label"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/sentiment", json={
            "texts": ["This product is absolutely amazing, best purchase ever!"]
        })

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["results"][0]["label"] == "positive"
    assert data["results"][0]["confidence"] > 0.5


@pytest.mark.asyncio
async def test_sentiment_negative():
    """Negative review text should return negative label"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/sentiment", json={
            "texts": ["Terrible quality, complete waste of money, do not buy."]
        })

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["results"][0]["label"] == "negative"
    assert data["results"][0]["confidence"] > 0.5


@pytest.mark.asyncio
async def test_sentiment_batch():
    """Batch input should return results for all texts"""
    texts = [
        "Great product, highly recommend!",
        "Worst purchase I ever made.",
        "Decent quality for the price.",
        "Absolutely love this, will buy again!"
    ]
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/sentiment", json={"texts": texts})

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 4
    assert len(data["results"]) == 4

    for result in data["results"]:
        assert "label" in result
        assert "confidence" in result
        assert result["label"] in ["positive", "negative"]


@pytest.mark.asyncio
async def test_sentiment_empty_input():
    """Empty texts list should return 422 validation error"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/sentiment", json={"texts": []})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_sentiment_response_structure():
    """Response should have correct structure"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/sentiment", json={
            "texts": ["Good product overall."]
        })

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total" in data

    result = data["results"][0]
    assert "text" in result
    assert "label" in result
    assert "confidence" in result
    assert isinstance(result["confidence"], float)