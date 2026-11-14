"""
BhashaVerse - FastAPI Application Entrypoint
Provides high-performance RESTful APIs for the multilingual Indian proverbs platform.
"""

from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Apply Windows socket protection immediately
import Backend.utils.windows_patch  # noqa: F401

from Backend.config import (
    APP_NAME,
    APP_TAGLINE,
    APP_VERSION,
    CORS_ORIGINS,
    API_PREFIX,
)
from Backend.database import init_db, seed_default_proverbs, get_statistics
from Backend.schemas import HealthResponse
from Backend.routes.proverbs import router as proverbs_router
from Backend.routes.chat import router as chat_router
from Backend.routes.analytics import router as analytics_router
from Backend.routes.moderation import router as moderation_router
from Backend.routes.exports import router as exports_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler: initializes the SQLite schema and seeds
    the baseline multilingual corpus if needed upon server startup.
    """
    init_db()
    seed_default_proverbs()
    yield


app = FastAPI(
    title=f"{APP_NAME} API",
    description=f"RESTful Backend for {APP_NAME} - {APP_TAGLINE}",
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for frontend and third-party integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules under /api
app.include_router(proverbs_router, prefix=API_PREFIX)
app.include_router(chat_router, prefix=API_PREFIX)
app.include_router(analytics_router, prefix=API_PREFIX)
app.include_router(moderation_router, prefix=API_PREFIX)
app.include_router(exports_router, prefix=API_PREFIX)


@app.get("/", tags=["Root"])
def root():
    """Root endpoint welcoming clients and directing to documentation."""
    return {
        "app": APP_NAME,
        "tagline": APP_TAGLINE,
        "version": APP_VERSION,
        "documentation": "/docs",
        "api_endpoints": f"{API_PREFIX}/proverbs",
    }


@app.get(f"{API_PREFIX}/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """System health check and database connectivity probe."""
    try:
        stats = get_statistics()
        db_ok = True
        count = stats.get("total_submissions", 0)
    except Exception:
        db_ok = False
        count = 0

    return HealthResponse(
        status="healthy" if db_ok else "degraded",
        app=APP_NAME,
        version=APP_VERSION,
        database_connected=db_ok,
        total_proverbs=count,
    )


def start():
    """Convenience entrypoint for launching via CLI or pyproject."""
    uvicorn.run("Backend.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    start()

