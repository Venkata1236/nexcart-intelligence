import httpx
from loguru import logger
from langchain.tools import tool


BASE_URL = "http://localhost:8000"


@tool
def get_recommendations(user_id: str) -> str:
    """
    Get personalized product recommendations for a user.
    Use this when the user asks for product suggestions or recommendations.
    Input: user_id string
    Output: formatted list of recommended products with ratings
    """
    try:
        response = httpx.post(
            f"{BASE_URL}/recommend",
            json={"user_id": user_id, "n": 5},
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()

        recommendations = data["recommendations"]
        cold_start = data["cold_start"]

        if not recommendations:
            return "No recommendations found for this user."

        lines = []
        if cold_start:
            lines.append("🆕 New user — showing popular products:\n")
        else:
            lines.append("🎯 Personalized recommendations:\n")

        for i, rec in enumerate(recommendations, 1):
            gem = " 💎 Hidden Gem" if rec["is_hidden_gem"] else ""
            lines.append(
                f"{i}. Product: {rec['product_id']}"
                f" | Rating: {rec['predicted_rating']:.1f}/5"
                f" | Reviews: {rec['review_count']}"
                f"{gem}"
            )

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"RecommendationTool failed: {e}")
        return f"Could not fetch recommendations: {str(e)}"


@tool
def search_by_sentiment(query: str) -> str:
    """
    Search for products by sentiment analysis on their reviews.
    Use this when user asks about product quality, reviews, or sentiment.
    Input: product description or category query
    Output: sentiment analysis results for matching products
    """
    try:
        # Use sentiment endpoint to analyze query intent
        response = httpx.post(
            f"{BASE_URL}/sentiment",
            json={"texts": [query]},
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()

        result = data["results"][0]
        label = result["label"]
        confidence = result["confidence"]

        # Return formatted sentiment context
        return (
            f"Query sentiment: {label} (confidence: {confidence:.0%})\n"
            f"For finding products with positive reviews, "
            f"use the get_product_detail tool with specific product IDs.\n"
            f"Query analyzed: '{query}'"
        )

    except Exception as e:
        logger.error(f"SentimentSearchTool failed: {e}")
        return f"Could not analyze sentiment: {str(e)}"


@tool
def get_product_detail(product_id: str) -> str:
    """
    Get detailed information about a specific product including sentiment summary.
    Use this when user asks about a specific product's reviews or quality.
    Input: product_id string
    Output: product details with sentiment breakdown and sample reviews
    """
    try:
        response = httpx.get(
            f"{BASE_URL}/product/{product_id}",
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()

        sentiment = data["sentiment_summary"]
        positive_pct = sentiment["positive_pct"] * 100
        negative_pct = sentiment["negative_pct"] * 100

        lines = [
            f"📦 Product: {data['product_id']}",
            f"⭐ Avg Rating: {data['avg_rating']:.1f}/5",
            f"📝 Total Reviews: {data['review_count']}",
            f"",
            f"😊 Positive: {positive_pct:.0f}%",
            f"😞 Negative: {negative_pct:.0f}%",
            f"",
            f"✅ Top positive phrases: {', '.join(sentiment['top_positive_phrases'])}",
            f"❌ Top negative phrases: {', '.join(sentiment['top_negative_phrases'])}",
        ]

        # Add sample reviews
        if data["sample_reviews"]:
            lines.append(f"\n📖 Sample Reviews:")
            for review in data["sample_reviews"][:3]:
                lines.append(
                    f"  [{review['sentiment'].upper()}] "
                    f"{review['text'][:100]}..."
                )

        return "\n".join(lines)

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Product {product_id} not found in our database."
        return f"Could not fetch product details: {str(e)}"
    except Exception as e:
        logger.error(f"ProductDetailTool failed: {e}")
        return f"Could not fetch product details: {str(e)}"