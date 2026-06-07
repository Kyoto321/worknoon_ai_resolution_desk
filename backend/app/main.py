"""
WorkNoon AI Support Assistant — FastAPI Application Entry Point.

Architecture:
  - FastAPI with async support
  - SQLAlchemy ORM (SQLite, WAL mode)
  - Gemini AI with structured output
  - Policy Engine for hallucination prevention
  - Rate limiting via SlowAPI
  - Comprehensive CORS configuration
  - Structured logging
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import engine, Base
from app.models import Customer, Order, SupportPolicy, SupportRequest, ConversationHistory  # noqa: F401
from app.routers import customers_router, orders_router, support_router, policies_router

# ── Logging Setup ─────────────────────────────────────────────────────────────
settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan (startup/shutdown) ───────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup if they don't exist."""
    logger.info("Starting %s...", settings.app_name)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified.")
    yield
    logger.info("Shutting down %s.", settings.app_name)


# ── FastAPI App ───────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    description=(
        "AI-Powered Customer Support Assistant. "
        "Evaluates support requests against company policies using Google Gemini AI."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS Middleware ───────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ── Request Logging Middleware ────────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every request with method, path, status, and duration."""
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s → %d (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


# ── Global Exception Handler ──────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catches unhandled exceptions.
    Never exposes stack traces to clients in production.
    """
    logger.error("Unhandled exception on %s: %s", request.url.path, str(exc), exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred. Please try again later.",
            "path": str(request.url.path),
        },
    )


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(customers_router)
app.include_router(orders_router)
app.include_router(support_router)
app.include_router(policies_router)


# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["system"], summary="Health check")
def health_check():
    """Returns application health status."""
    has_api_key = (
        settings.gemini_api_key
        and settings.gemini_api_key.strip()
        and settings.gemini_api_key != "your_gemini_api_key_here"
    )
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": "1.0.0",
        "environment": settings.app_env,
        "ai_configured": bool(has_api_key),
    }


@app.get("/", tags=["system"], summary="Root")
def root():
    """API root — returns basic info and docs link."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "docs": "/docs",
        "health": "/health",
    }
