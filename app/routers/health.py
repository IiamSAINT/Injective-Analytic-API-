"""
Health Router - API health check endpoints
"""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.injective_client import get_injective_client
from app.utils.cache import get_cache_stats

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: str = "1.0.0"


class InjectiveHealthResponse(BaseModel):
    """Injective connectivity check response."""
    status: str
    connected: bool
    endpoint: str
    timestamp: datetime


class DetailedHealthResponse(HealthResponse):
    """Detailed health response with cache stats."""
    cache: dict


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Basic API health check.
    
    Returns the current API status and timestamp.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc)
    )


@router.get("/health/injective", response_model=InjectiveHealthResponse)
async def injective_health_check():
    """
    Check connectivity to Injective network.
    
    Returns whether the API can successfully connect to Injective's LCD endpoint.
    """
    client = get_injective_client()
    is_connected = await client.health_check()
    
    return InjectiveHealthResponse(
        status="connected" if is_connected else "disconnected",
        connected=is_connected,
        endpoint=client.lcd_url,
        timestamp=datetime.now(timezone.utc)
    )


@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check():
    """
    Detailed health check with cache statistics.
    
    Returns API status, Injective connectivity, and cache statistics.
    """
    return DetailedHealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        cache=get_cache_stats()
    )
