from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "NexCart Intelligence"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/nexcart"
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_TTL: int = 3600
    GROQ_API_KEY: str = ""
    SVD_MODEL_PATH: str = "saved_models/svd_model.pkl"
    SENTIMENT_MODEL_PATH: str = "saved_models/sentiment_model"
    FAISS_INDEX_PATH: str = "faiss_index/"
    RECOMMENDATION_COUNT: int = 10
    SENTIMENT_BATCH_SIZE: int = 32
    SENTIMENT_MAX_LENGTH: int = 256
    MIN_REVIEWS_FOR_SENTIMENT: int = 5
    COLD_START_THRESHOLD: int = 5

    model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    case_sensitive=True,
    extra="ignore"
)


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()