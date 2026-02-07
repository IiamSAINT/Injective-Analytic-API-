"""
Analytics Router - Market analytics endpoints
"""
from fastapi import APIRouter, HTTPException, Query

from app.services.analytics_service import get_analytics_service
from app.models.analytics import (
    AnalyticsOverview, VolatilityMetrics, LiquidityMetrics,
    MarketHealthIndicator, TopMoversResponse
)

router = APIRouter()


@router.get("/analytics/overview", response_model=AnalyticsOverview)
async def get_analytics_overview():
    """
    Get global market analytics overview.
    
    Returns comprehensive market statistics including:
    - Total market counts (spot/derivative)
    - Total 24h trading volume
    - Top gainers and losers
    - Volume leaders
    
    This endpoint provides a snapshot of the entire Injective exchange ecosystem.
    """
    service = get_analytics_service()
    return await service.get_overview()


@router.get("/analytics/top-movers", response_model=TopMoversResponse)
async def get_top_movers(
    limit: int = Query(5, ge=1, le=20, description="Number of movers to return")
):
    """
    Get top price movers in the last 24 hours.
    
    Returns the markets with the largest positive and negative price changes.
    
    **Query Parameters:**
    - `limit`: Number of gainers/losers to return (1-20, default: 5)
    """
    service = get_analytics_service()
    return await service.get_top_movers(limit)


@router.get("/analytics/{market_id}/volatility", response_model=VolatilityMetrics)
async def get_volatility(market_id: str):
    """
    Get volatility metrics for a specific market.
    
    Returns volatility analysis including:
    - Standard deviation of price movements
    - 24h high/low range
    - Volatility as percentage of average price
    
    **Path Parameters:**
    - `market_id`: The unique Injective market identifier
    
    **Use Cases:**
    - Risk assessment for trading strategies
    - Identifying stable vs. volatile markets
    - Setting appropriate stop-loss levels
    """
    service = get_analytics_service()
    result = await service.get_volatility(market_id)
    
    if not result:
        raise HTTPException(status_code=404, detail=f"Market {market_id} not found")
    
    return result


@router.get("/analytics/{market_id}/liquidity", response_model=LiquidityMetrics)
async def get_liquidity(market_id: str):
    """
    Get liquidity metrics for a specific market.
    
    Returns liquidity analysis including:
    - Liquidity score (0-100)
    - Bid and ask depth in quote currency
    - Bid-ask spread in basis points
    - Depth ratio (buy/sell balance)
    
    **Path Parameters:**
    - `market_id`: The unique Injective market identifier
    
    **Liquidity Score Interpretation:**
    - 80-100: Excellent liquidity, tight spreads
    - 60-79: Good liquidity, suitable for most trades
    - 40-59: Moderate liquidity, larger trades may have slippage
    - Below 40: Low liquidity, trade with caution
    """
    service = get_analytics_service()
    result = await service.get_liquidity(market_id)
    
    if not result:
        raise HTTPException(status_code=404, detail=f"Market {market_id} not found")
    
    return result


@router.get("/analytics/{market_id}/health", response_model=MarketHealthIndicator)
async def get_market_health(market_id: str):
    """
    Get overall health indicator for a specific market.
    
    Returns a composite health score based on:
    - Liquidity (40% weight)
    - Volatility (30% weight) - moderate volatility is preferred
    - Trading activity (30% weight)
    
    **Path Parameters:**
    - `market_id`: The unique Injective market identifier
    
    **Health Status:**
    - `healthy`: Score >= 70 - Market is active and liquid
    - `moderate`: Score 40-69 - Market is functional but with some concerns
    - `weak`: Score < 40 - Market may have liquidity or activity issues
    """
    service = get_analytics_service()
    result = await service.get_market_health(market_id)
    
    if not result:
        raise HTTPException(status_code=404, detail=f"Market {market_id} not found")
    
    return result
