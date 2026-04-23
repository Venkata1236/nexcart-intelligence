from fastapi import APIRouter, HTTPException
from loguru import logger
import pickle
import pandas as pd
from pathlib import Path
from collections import Counter

from app.models.schemas import ProductResponse, SentimentSummary, SampleReview
from app.ml.sentiment import sentiment_analyzer

router = APIRouter()

# Load reviews dataframe once at module level
_reviews_df: pd.DataFrame | None = None


def get_reviews_df() -> pd.DataFrame | None:
    """Load reviews CSV once and cache in memory"""
    global _reviews_df
    if _reviews_df is None:
        try:
            reviews_path = Path("data/Reviews.csv")
            if reviews_path.exists():
                _reviews_df = pd.read_csv(reviews_path)[
                    ['ProductId', 'Score', 'Text', 'Summary']
                ].dropna()
                logger.info(f"Reviews dataframe loaded — {len(_reviews_df)} rows")
            else:
                logger.warning("Reviews.csv not found")
        except Exception as e:
            logger.error(f"Failed to load reviews dataframe: {e}")
    return _reviews_df


def extract_top_phrases(texts: list[str], n: int = 3) -> list[str]:
    """
    Extract most common meaningful phrases from review texts.
    Simple word frequency approach — no NLP library needed.
    """
    # Common stopwords to ignore
    stopwords = {
        "the", "a", "an", "is", "it", "this", "and", "or", "but",
        "in", "on", "at", "to", "for", "of", "with", "are", "was",
        "i", "my", "we", "they", "have", "has", "be", "not", "so",
        "very", "just", "really", "that", "these", "those", "its"
    }

    word_counts = Counter()
    for text in texts:
        words = text.lower().split()
        for word in words:
            # Clean punctuation
            word = word.strip(".,!?;:'\"()")
            if len(word) > 3 and word not in stopwords:
                word_counts[word] += 1

    return [word for word, _ in word_counts.most_common(n)]


@router.get("/product/{product_id}", response_model=ProductResponse)
async def get_product_detail(product_id: str):
    """
    Get full product detail with sentiment summary.

    - Review count + avg rating
    - Sentiment breakdown: positive % / negative %
    - Top positive and negative phrases
    - Sample reviews with sentiment labels
    """
    logger.info(f"Product detail request — product_id: {product_id}")

    # Load reviews
    df = get_reviews_df()
    if df is None:
        raise HTTPException(
            status_code=503,
            detail="Reviews data not available"
        )

    # Filter reviews for this product
    product_reviews = df[df["ProductId"] == product_id]

    if product_reviews.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Product {product_id} not found"
        )

    # Basic stats
    review_count = len(product_reviews)
    avg_rating = round(float(product_reviews["Score"].mean()), 2)

    # Get review texts
    review_texts = product_reviews["Text"].tolist()

    # Limit to 100 reviews for sentiment analysis speed
    sample_texts = review_texts[:100]

    # Run sentiment on all sampled reviews
    if sentiment_analyzer.is_loaded:
        sentiment_results = sentiment_analyzer.predict_batch(sample_texts)
    else:
        # Fallback — use score as proxy for sentiment
        sentiment_results = [
            {
                "text": row["Text"],
                "label": "positive" if row["Score"] >= 4 else "negative",
                "confidence": 0.85
            }
            for _, row in product_reviews.head(100).iterrows()
        ]

    # Calculate sentiment breakdown
    positive_results = [r for r in sentiment_results if r["label"] == "positive"]
    negative_results = [r for r in sentiment_results if r["label"] == "negative"]

    positive_pct = round(len(positive_results) / len(sentiment_results), 4)
    negative_pct = round(len(negative_results) / len(sentiment_results), 4)

    # Extract top phrases from positive and negative reviews
    positive_texts = [r["text"] for r in positive_results]
    negative_texts = [r["text"] for r in negative_results]

    top_positive_phrases = extract_top_phrases(positive_texts, n=3)
    top_negative_phrases = extract_top_phrases(negative_texts, n=3)

    # Build sample reviews — 5 positive + 5 negative
    sample_reviews = []
    for r in positive_results[:5]:
        sample_reviews.append(SampleReview(
            text=r["text"][:200],
            score=int(product_reviews[
                product_reviews["Text"] == r["text"]
            ]["Score"].values[0]) if r["text"] in product_reviews["Text"].values else 5,
            sentiment="positive",
            confidence=r["confidence"]
        ))
    for r in negative_results[:5]:
        sample_reviews.append(SampleReview(
            text=r["text"][:200],
            score=int(product_reviews[
                product_reviews["Text"] == r["text"]
            ]["Score"].values[0]) if r["text"] in product_reviews["Text"].values else 1,
            sentiment="negative",
            confidence=r["confidence"]
        ))

    # Build final response
    response = ProductResponse(
        product_id=product_id,
        review_count=review_count,
        avg_rating=avg_rating,
        sentiment_summary=SentimentSummary(
            positive_pct=positive_pct,
            negative_pct=negative_pct,
            top_positive_phrases=top_positive_phrases,
            top_negative_phrases=top_negative_phrases
        ),
        sample_reviews=sample_reviews
    )

    logger.info(f"Product detail served — {product_id}: {review_count} reviews, {positive_pct:.0%} positive")
    return response