"""
Injective Market & Network Data API - Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import markets, analytics, health, ninja, premium, supply

settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(markets.router, prefix="/api/v1", tags=["Markets"])
app.include_router(analytics.router, prefix="/api/v1", tags=["Analytics"])
app.include_router(ninja.router, prefix="/api/v1", tags=["Ninja Analytics"])
app.include_router(premium.router, prefix="/api/v1", tags=["Premium (Gated)"])
app.include_router(supply.router, prefix="/api/v1", tags=["Supply & Economics"])


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "docs": "/docs",
        "health": "/api/v1/health"
    }
