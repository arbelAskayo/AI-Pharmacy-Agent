"""
FastAPI application entry point.
Pharmacy Assistant Chat Backend.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from logging_config import configure_logging, get_logger
from database import init_db
from seed_data import seed_database
from routers import health, medications, chat_debug


# Configure logging first
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - runs on startup and shutdown."""
    # Startup
    logger.info("application_starting", app_name=settings.app_name)
    
    # Initialize database and seed if needed
    init_db()
    seeded = seed_database()
    if seeded:
        logger.info("database_seeded_on_startup")
    
    logger.info("application_started", 
                openai_configured=settings.openai_configured,
                cors_origins=settings.cors_origins)
    
    yield
    
    # Shutdown
    logger.info("application_shutting_down")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI-powered pharmacy assistant chat backend with tool calling support.",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(medications.router)
app.include_router(chat_debug.router)


@app.get("/")
async def root():
    """Root endpoint - basic info."""
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/health",
    }

