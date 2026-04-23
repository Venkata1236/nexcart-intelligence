import torch
import pickle
import numpy as np
from pathlib import Path
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from loguru import logger
from app.core.config import settings


class SentimentAnalyzer:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def load(self):
        """Load fine-tuned DistilBERT model + tokenizer from saved_models/"""
        try:
            model_path = Path(settings.SENTIMENT_MODEL_PATH)
            if not model_path.exists():
                logger.warning(f"Sentiment model not found at {model_path} — using pretrained base")
                model_path = "distilbert-base-uncased"

            self.tokenizer = DistilBertTokenizer.from_pretrained(str(model_path))
            self.model = DistilBertForSequenceClassification.from_pretrained(str(model_path))
            self.model.to(self.device)
            self.model.eval()

            self.is_loaded = True
            logger.info(f"Sentiment model loaded ✅ — device: {self.device}")
            return True

        except Exception as e:
            logger.error(f"Failed to load sentiment model: {e}")
            return False

    def predict(self, text: str) -> dict:
        """
        Predict sentiment for a single text.
        Returns label and confidence score.
        """
        if not self.is_loaded:
            logger.error("Sentiment model not loaded — call load() first")
            return {"label": "positive", "confidence": 0.0}

        try:
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=settings.SENTIMENT_MAX_LENGTH,
                padding=True
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs)

            probs = torch.softmax(outputs.logits, dim=-1)
            predicted_class = torch.argmax(probs).item()
            confidence = probs[0][predicted_class].item()

            return {
                "label": "positive" if predicted_class == 1 else "negative",
                "confidence": round(confidence, 4)
            }

        except Exception as e:
            logger.error(f"Sentiment prediction failed: {e}")
            return {"label": "positive", "confidence": 0.0}

    def predict_batch(self, texts: list[str]) -> list[dict]:
        """
        Batch inference — process multiple texts at once.
        Splits into chunks of SENTIMENT_BATCH_SIZE for memory efficiency.
        """
        if not self.is_loaded:
            logger.error("Sentiment model not loaded")
            return []

        results = []
        batch_size = settings.SENTIMENT_BATCH_SIZE

        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i: i + batch_size]

            try:
                inputs = self.tokenizer(
                    batch,
                    return_tensors="pt",
                    truncation=True,
                    max_length=settings.SENTIMENT_MAX_LENGTH,
                    padding=True
                ).to(self.device)

                with torch.no_grad():
                    outputs = self.model(**inputs)

                probs = torch.softmax(outputs.logits, dim=-1)
                predicted_classes = torch.argmax(probs, dim=-1).tolist()
                confidences = probs.max(dim=-1).values.tolist()

                for text, pred_class, confidence in zip(batch, predicted_classes, confidences):
                    results.append({
                        "text": text,
                        "label": "positive" if pred_class == 1 else "negative",
                        "confidence": round(confidence, 4)
                    })

            except Exception as e:
                logger.error(f"Batch sentiment prediction failed at index {i}: {e}")
                # Add fallback results for failed batch
                for text in batch:
                    results.append({
                        "text": text,
                        "label": "positive",
                        "confidence": 0.0
                    })

        logger.info(f"Batch sentiment done — {len(results)} texts processed")
        return results

    def get_sentiment_score(self, texts: list[str]) -> float:
        """
        Get aggregate sentiment score for a list of texts.
        Returns float 0-1 (1 = all positive, 0 = all negative).
        Used by /product endpoint for sentiment summary.
        """
        if not texts:
            return 0.0

        results = self.predict_batch(texts)
        positive_count = sum(1 for r in results if r["label"] == "positive")
        return round(positive_count / len(results), 4)


# Singleton — loaded once at startup
sentiment_analyzer = SentimentAnalyzer()