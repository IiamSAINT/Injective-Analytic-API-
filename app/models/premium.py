"""
Pydantic models for Premium features
"""
from typing import List
from pydantic import BaseModel
from app.models.ninja import NinjaTrader


class WhaleResponse(BaseModel):
    """Response model for whale watch."""
    whales: List[NinjaTrader]


class TagRequest(BaseModel):
    """Request model for adding tags."""
    address: str
    tag: str
