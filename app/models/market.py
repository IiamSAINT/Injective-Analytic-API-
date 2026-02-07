"""
Pydantic models for market data
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class TokenMeta(BaseModel):
    """Token metadata."""
    name: str
    symbol: str
    decimals: int
    logo: Optional[str] = None


class MarketSummary(BaseModel):
    """Summary information for a market."""
    market_id: str = Field(..., description="Unique market identifier")
    ticker: str = Field(..., description="Market ticker symbol")
    market_type: str = Field(..., description="Type of market: spot or derivative")
    base_token: str = Field(..., description="Base token symbol")
    quote_token: str = Field(..., description="Quote token symbol")
    last_price: Optional[float] = Field(None, description="Last traded price")
    price_change_24h: Optional[float] = Field(None, description="24h price change percentage")
    volume_24h: Optional[float] = Field(None, description="24h trading volume in quote currency")
    high_24h: Optional[float] = Field(None, description="24h high price")
    low_24h: Optional[float] = Field(None, description="24h low price")
    status: str = Field("active", description="Market status")


class MarketDetail(MarketSummary):
    """Detailed market information."""
    maker_fee_rate: Optional[float] = Field(None, description="Maker fee rate")
    taker_fee_rate: Optional[float] = Field(None, description="Taker fee rate")
    min_price_tick_size: Optional[float] = Field(None, description="Minimum price tick size")
    min_quantity_tick_size: Optional[float] = Field(None, description="Minimum quantity tick size")
    base_decimals: int = Field(18, description="Base token decimals")
    quote_decimals: int = Field(6, description="Quote token decimals")


class OrderbookLevel(BaseModel):
    """Single level in the orderbook."""
    price: float = Field(..., description="Price at this level")
    quantity: float = Field(..., description="Quantity at this level")
    total: float = Field(..., description="Cumulative quantity up to this level")


class Orderbook(BaseModel):
    """Orderbook snapshot."""
    market_id: str
    timestamp: datetime
    bids: List[OrderbookLevel] = Field(default_factory=list, description="Buy orders (bids)")
    asks: List[OrderbookLevel] = Field(default_factory=list, description="Sell orders (asks)")
    spread: Optional[float] = Field(None, description="Bid-ask spread")
    spread_percentage: Optional[float] = Field(None, description="Spread as percentage of mid price")
    mid_price: Optional[float] = Field(None, description="Mid price between best bid and ask")


class Trade(BaseModel):
    """A single trade."""
    trade_id: str
    market_id: str
    price: float
    quantity: float
    side: str = Field(..., description="Trade side: buy or sell")
    timestamp: datetime
    fee: Optional[float] = None


class TradesResponse(BaseModel):
    """Response containing a list of trades."""
    market_id: str
    trades: List[Trade]
    total: int


class MarketsResponse(BaseModel):
    """Response containing list of markets."""
    markets: List[MarketSummary]
    total: int
    spot_count: int
    derivative_count: int
