"""
Pydantic models for Ninja Analytics
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class NinjaTrader(BaseModel):
    """Active participant/trader model."""
    address: str = Field(..., description="Wallet address")
    volume_24h_est: float = Field(0.0, description="Estimated 24h volume (in quote units)")
    transaction_count_recent: int = Field(0, description="Recent transaction count (from blocks)")
    tags: List[str] = Field(default_factory=list, description="Associated tags (e.g. Whale, CEX)")
    ninja_score: float = Field(..., description="Activity score (0-100)")


class AddressCheckResponse(BaseModel):
    """Response for address check."""
    address: str
    tags: List[str]
    is_known_entity: bool
