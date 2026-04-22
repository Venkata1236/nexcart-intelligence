from pydantic_settings import BaseSettings  # Base class for managing app settings with validation and env support
from functools import lru_cache             # Decorator to cache function results (avoids reloading settings repeatedly)


class Settings(BaseSettings):
    # -------------------------
    # App Configuration
    # -------------------------
    APP_NAME: str = "NexCart Intelligence"   # Application name
    VERSION: str = "1.0.0"                   # Application version
    ENVIRONMENT: str = "development"         # Current environment (development/staging/production)
    DEBUG: bool = True                       # Debug mode toggle

    # -------------------------
    # Database Configuration
    # -------------------------
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/nexcart"
    # Connection string for PostgreSQL using asyncpg driver

    # -------------------------
    # Redis Configuration
    # -------------------------
    REDIS_URL: str = "redis://localhost:6379" # Redis server connection URL
    REDIS_TTL: int = 3600                     # Cache expiration time (TTL) in seconds → 1 hour

    # -------------------------
    # Groq API Key
    # -------------------------
    GROQ_API_KEY: str = ""                    # Placeholder for Groq API key (to be set via .env)

    # -------------------------
    # Model Paths
    # -------------------------
    SVD_MODEL_PATH: str = "saved_models/svd_model.pkl"       # Path to saved recommendation model (SVD)
    SENTIMENT_MODEL_PATH: str = "saved_models/sentiment_model" # Path to sentiment analysis model directory
    FAISS_INDEX_PATH: str = "faiss_index/"                   # Path to FAISS vector index storage

    # -------------------------
    # ML Settings
    # -------------------------
    RECOMMENDATION_COUNT: int = 10            # Number of recommendations to generate per user
    SENTIMENT_BATCH_SIZE: int = 32            # Batch size for sentiment model inference
    SENTIMENT_MAX_LENGTH: int = 256           # Max token length for sentiment model input
    MIN_REVIEWS_FOR_SENTIMENT: int = 5        # Minimum reviews required before running sentiment analysis

    # -------------------------
    # Cold Start Handling
    # -------------------------
    COLD_START_THRESHOLD: int = 5             # Users with < 5 reviews are treated as cold start cases

    # -------------------------
    # Pydantic Config
    # -------------------------
    class Config:
        env_file = ".env"                     # Load environment variables from .env file
        case_sensitive = True                 # Environment variable names are case-sensitive
