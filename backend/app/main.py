from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from app.core.config import settings
from app.ml.collaborative import collaborative_filter
from app.ml.sentiment import sentiment_analyzer
from app.models.schemas import HealthResponse
from app.routes import recommend, sentiment, product
from app.routes import recommend, sentiment, product, agent


# ─────────────────────────────────────────
# LIFESPAN — Startup + Shutdown
# ─────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──
    logger.info("Starting NexCart Intelligence API...")

    # Load SVD model
    logger.info("Loading SVD collaborative filter model...")
    svd_loaded = collaborative_filter.load()
    if svd_loaded:
        logger.info("SVD model loaded ✅")
    else:
        logger.warning("SVD model failed to load ⚠️ — /recommend will return 503")

    # Load DistilBERT sentiment model
    logger.info("Loading DistilBERT sentiment model...")
    sentiment_loaded = sentiment_analyzer.load()
    if sentiment_loaded:
        logger.info("Sentiment model loaded ✅")
    else:
        logger.warning("Sentiment model failed to load ⚠️ — /sentiment will use fallback")

    logger.info("NexCart Intelligence API ready 🚀")

    yield

    # ── Shutdown ──
    logger.info("Shutting down NexCart Intelligence API...")


# ─────────────────────────────────────────
# APP INSTANCE
# ─────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Production-grade retail AI — SVD recommendations + DistilBERT sentiment + LangChain agent",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# ─────────────────────────────────────────
# CORS MIDDLEWARE
# ─────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────
# ROUTERS
# ─────────────────────────────────────────

app.include_router(recommend.router, tags=["Recommendations"])
app.include_router(sentiment.router, tags=["Sentiment"])
app.include_router(product.router,   tags=["Products"])
app.include_router(agent.router, tags=["Agent"])


# ─────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health + model load status"""
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        models_loaded={
            "svd": collaborative_filter.is_loaded,
            "sentiment": sentiment_analyzer.is_loaded
        }
    )


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }