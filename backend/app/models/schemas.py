from pydantic import BaseModel, Field   # BaseModel defines structured data models with validation
from typing import Optional             # Optional type hint for nullable fields


# ─────────────────────────────────────────
# RECOMMENDATION SCHEMAS
# ─────────────────────────────────────────

class RecommendRequest(BaseModel):
    user_id: str = Field(..., example="A3SGXH7AUHU8GW")  # User identifier (required)
    n: int = Field(default=10, ge=1, le=50)              # Number of recommendations (default 10, between 1–50)


class RecommendedProduct(BaseModel):
    product_id: str             # Product identifier
    predicted_rating: float     # Predicted rating from recommendation model
    sentiment_score: float      # Sentiment score from sentiment analysis
    review_count: int           # Number of reviews for this product
    is_hidden_gem: bool         # True if product has high sentiment but low review count


class RecommendResponse(BaseModel):
    user_id: str                                # User identifier
    recommendations: list[RecommendedProduct]   # List of recommended products
    cold_start: bool                            # True if fallback (e.g., TF-IDF) was used due to insufficient data


# ─────────────────────────────────────────
# SENTIMENT SCHEMAS
# ─────────────────────────────────────────

class SentimentRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1, max_length=100)  
    # List of texts to analyze (between 1–100 items)


class SentimentResult(BaseModel):
    text: str             # Original text
    label: str            # Sentiment label ("positive" or "negative")
    confidence: float     # Confidence score of prediction


class SentimentResponse(BaseModel):
    results: list[SentimentResult]  # List of sentiment analysis results
    total: int                      # Total number of texts analyzed


# ─────────────────────────────────────────
# PRODUCT SCHEMAS
# ─────────────────────────────────────────

class SentimentSummary(BaseModel):
    positive_pct: float             # Percentage of positive reviews
    negative_pct: float             # Percentage of negative reviews
    top_positive_phrases: list[str] # Common positive phrases extracted
    top_negative_phrases: list[str] # Common negative phrases extracted


class SampleReview(BaseModel):
    text: str           # Review text
    score: int          # Numeric rating (e.g., 1–5 stars)
    sentiment: str      # Sentiment label ("positive"/"negative")
    confidence: float   # Confidence score of sentiment prediction


class ProductResponse(BaseModel):
    product_id: str                 # Product identifier
    review_count: int               # Total number of reviews
    avg_rating: float               # Average rating across reviews
    sentiment_summary: SentimentSummary  # Aggregated sentiment summary
    sample_reviews: list[SampleReview]   # Example reviews with sentiment analysis


# ─────────────────────────────────────────
# AGENT SCHEMAS
# ─────────────────────────────────────────

class AgentQueryRequest(BaseModel):
    user_id: str = Field(..., example="A3SGXH7AUHU8GW")  
    # User identifier
    query: str = Field(..., example="show me products with positive reviews under high rating")  
    # Natural language query


class AgentQueryResponse(BaseModel):
    response: str              # Agent’s textual response
    products_mentioned: list[str]  # List of product IDs mentioned in the response


# ─────────────────────────────────────────
# HEALTH SCHEMA
# ─────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str                # Application health status ("ok", "error")
    version: str               # Current app version
    environment: str           # Environment ("development", "production")
    models_loaded: dict[str, bool]  # Dictionary showing which models are loaded (True/False)
