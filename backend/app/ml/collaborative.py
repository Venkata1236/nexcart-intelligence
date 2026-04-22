import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from loguru import logger
from app.core.config import settings


class CollaborativeFilter:
    def __init__(self):
        self.model = None
        self.product_meta = None
        self.known_users = None
        self.known_products = None
        self.is_loaded = False

    def load(self):
        """Load SVD model + all metadata from saved_models/"""
        try:
            # Load SVD model
            svd_path = Path(settings.SVD_MODEL_PATH)
            if not svd_path.exists():
                logger.error(f"SVD model not found at {svd_path}")
                return False

            with open(svd_path, "rb") as f:
                self.model = pickle.load(f)

            # Load product metadata
            meta_path = Path("saved_models/product_meta.pkl")
            with open(meta_path, "rb") as f:
                self.product_meta = pickle.load(f)

            # Load known users
            users_path = Path("saved_models/known_users.pkl")
            with open(users_path, "rb") as f:
                self.known_users = pickle.load(f)

            # Load known products
            products_path = Path("saved_models/known_products.pkl")
            with open(products_path, "rb") as f:
                self.known_products = pickle.load(f)

            self.is_loaded = True
            logger.info(f"SVD model loaded ✅ — {len(self.known_users)} users, {len(self.known_products)} products")
            return True

        except Exception as e:
            logger.error(f"Failed to load SVD model: {e}")
            return False

    def is_cold_start(self, user_id: str) -> bool:
        """Check if user is new — not in training data"""
        return user_id not in self.known_users

    def get_recommendations(self, user_id: str, n: int = 10) -> dict:
        """
        Get top-N product recommendations for a user.
        Returns cold_start=True if user is new.
        """
        if not self.is_loaded:
            logger.error("Model not loaded — call load() first")
            return {"recommendations": [], "cold_start": False}

        # Cold start — new user has no history
        if self.is_cold_start(user_id):
            logger.info(f"Cold start detected for user: {user_id}")
            return self._cold_start_recommendations(n)

        # SVD inference — predict rating for all known products
        predictions = []
        for product_id in self.known_products:
            pred = self.model.predict(user_id, product_id)
            predictions.append((product_id, pred.est))

        # Sort by predicted rating descending
        predictions.sort(key=lambda x: x[1], reverse=True)
        top_n = predictions[:n]

        # Build recommendation objects
        recommendations = []
        for product_id, predicted_rating in top_n:
            meta = self._get_product_meta(product_id)
            recommendations.append({
                "product_id": product_id,
                "predicted_rating": round(predicted_rating, 3),
                "sentiment_score": 0.0,   # filled by /recommend route
                "review_count": meta["review_count"],
                "is_hidden_gem": self._is_hidden_gem(
                    predicted_rating,
                    meta["review_count"]
                )
            })

        logger.info(f"SVD recommendations generated for user: {user_id}")
        return {"recommendations": recommendations, "cold_start": False}

    def _get_product_meta(self, product_id: str) -> dict:
        """Get review count + avg rating for a product"""
        row = self.product_meta[self.product_meta["ProductId"] == product_id]
        if row.empty:
            return {"review_count": 0, "avg_rating": 0.0}
        return {
            "review_count": int(row["review_count"].values[0]),
            "avg_rating": round(float(row["avg_rating"].values[0]), 3)
        }

    def _is_hidden_gem(self, predicted_rating: float, review_count: int) -> bool:
        """
        Hidden gem = high predicted rating + low visibility
        Threshold: predicted >= 4.0 AND review_count <= 50
        """
        return predicted_rating >= 4.0 and review_count <= 50

    def _cold_start_recommendations(self, n: int) -> dict:
        """
        Cold start fallback — return top-N products by avg_rating
        with minimum review_count for reliability.
        This is content-based — no user history needed.
        """
        # Filter products with at least 20 reviews for reliability
        reliable = self.product_meta[self.product_meta["review_count"] >= 20]

        # Sort by avg_rating descending
        top_products = reliable.sort_values("avg_rating", ascending=False).head(n)

        recommendations = []
        for _, row in top_products.iterrows():
            recommendations.append({
                "product_id": row["ProductId"],
                "predicted_rating": round(float(row["avg_rating"]), 3),
                "sentiment_score": 0.0,
                "review_count": int(row["review_count"]),
                "is_hidden_gem": False  # cold start products are popular, not hidden
            })

        logger.info(f"Cold start recommendations generated — {len(recommendations)} products")
        return {"recommendations": recommendations, "cold_start": True}


# Singleton — loaded once at startup, reused across all requests
collaborative_filter = CollaborativeFilter()