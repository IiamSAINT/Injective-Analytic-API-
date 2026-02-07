"""
Pydantic models for analytics data
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class VolatilityMetrics(BaseModel):
    """Volatility analysis for a market."""
    market_id: str
    ticker: str
    period: str = Field("24h", description="Analysis period")
    volatility: float = Field(..., description="Price volatility (standard deviation)")
    volatility_percentage: float = Field(..., description="Volatility as percentage of average price")
    high: float = Field(..., description="Highest price in period")
    low: float = Field(..., description="Lowest price in period")
    range_percentage: float = Field(..., description="Price range as percentage")
    average_price: float = Field(..., description="Average price in period")
    calculated_at: datetime


class LiquidityMetrics(BaseModel):
    """Liquidity analysis for a market."""
    market_id: str
    ticker: str
    liquidity_score: float = Field(..., ge=0, le=100, description="Liquidity score 0-100")
    bid_depth: float = Field(..., description="Total bid-side depth in quote currency")
    ask_depth: float = Field(..., description="Total ask-side depth in quote currency")
    total_depth: float = Field(..., description="Total orderbook depth")
    spread: float = Field(..., description="Current bid-ask spread")
    spread_bps: float = Field(..., description="Spread in basis points")
    depth_ratio: float = Field(..., description="Bid/Ask depth ratio")
    calculated_at: datetime


class MarketHealthIndicator(BaseModel):
    """Market health composite indicator."""
    market_id: str
    ticker: str
    health_score: float = Field(..., ge=0, le=100, description="Overall health score 0-100")
    liquidity_component: float = Field(..., description="Liquidity contribution to score")
    volatility_component: float = Field(..., description="Volatility contribution to score")
    activity_component: float = Field(..., description="Trading activity contribution")
    status: str = Field(..., description="Status: healthy, moderate, or weak")
    calculated_at: datetime


class MarketMover(BaseModel):
    """Market that moved significantly."""
    market_id: str
    ticker: str
    price_change_24h: float
    volume_24h: float
    last_price: float


class TopMoversResponse(BaseModel):
    """Top gainers and losers."""
    gainers: List[MarketMover]
    losers: List[MarketMover]
    timestamp: datetime


class VolumeLeader(BaseModel):
    """Market with high volume."""
    market_id: str
    ticker: str
    volume_24h: float
    volume_rank: int
    trade_count_24h: Optional[int] = None


class OverviewStats(BaseModel):
    """Global market overview statistics."""
    total_markets: int
    active_spot_markets: int
    active_derivative_markets: int
    total_volume_24h: float
    top_volume_market: Optional[str] = None
    average_spread_bps: float
    timestamp: datetime


class AnalyticsOverview(BaseModel):
    """Complete analytics overview."""
    stats: OverviewStats
    top_gainers: List[MarketMover]
    top_losers: List[MarketMover]
    volume_leaders: List[VolumeLeader]
