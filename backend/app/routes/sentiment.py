from fastapi import APIRouter, HTTPException
from loguru import logger

from app.models.schemas import SentimentRequest, SentimentResponse, SentimentResult
from app.ml.sentiment import sentiment_analyzer

router = APIRouter()


@router.post("/sentiment", response_model=SentimentResponse)
async def analyze_sentiment(request: SentimentRequest):
    """
    Batch sentiment analysis on a list of review texts.

    - Input:  list of text strings (max 100)
    - Output: label (positive/negative) + confidence per text
    """
    logger.info(f"Sentiment request — {len(request.texts)} texts")

    # Check model loaded
    if not sentiment_analyzer.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Sentiment model not loaded. Please wait for startup to complete."
        )

    # Validate input
    if not request.texts:
        raise HTTPException(
            status_code=400,
            detail="texts list cannot be empty"
        )

    # Run batch inference
    try:
        raw_results = sentiment_analyzer.predict_batch(request.texts)
    except Exception as e:
        logger.error(f"Sentiment batch inference failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Sentiment inference failed: {str(e)}"
        )

    # Build response objects
    results = [
        SentimentResult(
            text=r["text"],
            label=r["label"],
            confidence=r["confidence"]
        )
        for r in raw_results
    ]

    logger.info(f"Sentiment done — {len(results)} results returned")

    return SentimentResponse(
        results=results,
        total=len(results)
    )