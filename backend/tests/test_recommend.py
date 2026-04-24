import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_recommend_known_user():
    """Known user should get SVD recommendations with cold_start=False"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/recommend", json={
            "user_id": "A3SGXH7AUHU8GW",
            "n": 5
        })

    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert "cold_start" in data
    assert len(data["recommendations"]) <= 5

    # Each recommendation has required fields
    for rec in data["recommendations"]:
        assert "product_id" in rec
        assert "predicted_rating" in rec
        assert "sentiment_score" in rec
        assert "review_count" in rec
        assert "is_hidden_gem" in rec


@pytest.mark.asyncio
async def test_recommend_cold_start():
    """Unknown user should trigger cold start fallback"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/recommend", json={
            "user_id": "UNKNOWN_USER_XYZ_123",
            "n": 5
        })

    assert response.status_code == 200
    data = response.json()
    assert data["cold_start"] == True
    assert len(data["recommendations"]) > 0


@pytest.mark.asyncio
async def test_recommend_invalid_n():
    """n > 50 should return 422 validation error"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/recommend", json={
            "user_id": "A3SGXH7AUHU8GW",
            "n": 999
        })

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_health_check():
    """Health endpoint should return healthy status"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "models_loaded" in data
    assert "svd" in data["models_loaded"]
    assert "sentiment" in data["models_loaded"]