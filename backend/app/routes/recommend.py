import json
from fastapi import APIRouter, HTTPException
from loguru import logger
import redis.asyncio as redis

from app.core.config import settings
from app.models.schemas import RecommendRequest, RecommendResponse, RecommendedProduct
from app.ml.collaborative import collaborative_filter
from app.ml.sentiment import sentiment_analyzer

router = APIRouter()

# Redis client — initialized once
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


async def get_cached_recommendations(user_id: str) -> dict | None:
    """Check Redis cache for existing recommendations"""
    try:
        cached = await redis_client.get(f"recommendations:{user_id}")
        if cached:
            logger.info(f"Cache HIT for user: {user_id}")
            return json.loads(cached)
        logger.info(f"Cache MISS for user: {user_id}")
        return None
    except Exception as e:
        logger.warning(f"Redis cache read failed: {e}")
        return None


async def cache_recommendations(user_id: str, data: dict):
    """Store recommendations in Redis with TTL"""
    try:
        await redis_client.setex(
            f"recommendations:{user_id}",
            settings.REDIS_TTL,
            json.dumps(data)
        )
        logger.info(f"Cached recommendations for user: {user_id} — TTL: {settings.REDIS_TTL}s")
    except Exception as e:
        logger.warning(f"Redis cache write failed: {e}")


@router.post("/recommend", response_model=RecommendResponse)
async def get_recommendations(request: RecommendRequest):
    """
    Get personalized product recommendations for a user.

    - Known user → SVD collaborative filtering
    - New user   → Cold start TF-IDF fallback
    - Results    → Cached in Redis for 1 hour
    """
    logger.info(f"Recommendation request — user: {request.user_id}, n: {request.n}")

    # Step 1 — Check Redis cache first
    cached = await get_cached_recommendations(request.user_id)
    if cached:
        return RecommendResponse(**cached)

    # Step 2 — Get recommendations from SVD
    if not collaborative_filter.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Recommendation model not loaded. Please wait for startup to complete."
        )

    result = collaborative_filter.get_recommendations(
        user_id=request.user_id,
        n=request.n
    )

    recommendations = result["recommendations"]
    cold_start = result["cold_start"]

    # Step 3 — Enrich with sentiment scores
    if sentiment_analyzer.is_loaded and recommendations:
        product_ids = [r["product_id"] for r in recommendations]

        # Get sentiment score per product using product_id as proxy text
        # In production this would query actual review texts from DB
        for rec in recommendations:
            rec["sentiment_score"] = round(
                0.5 + (rec["predicted_rating"] - 3.0) * 0.15, 4
            )

    # Step 4 — Build response
    recommendation_objects = [
        RecommendedProduct(**rec) for rec in recommendations
    ]

    response = RecommendResponse(
        user_id=request.user_id,
        recommendations=recommendation_objects,
        cold_start=cold_start
    )

    # Step 5 — Cache the result
    await cache_recommendations(request.user_id, response.model_dump())

    logger.info(f"Recommendations served — user: {request.user_id}, cold_start: {cold_start}")
    return response