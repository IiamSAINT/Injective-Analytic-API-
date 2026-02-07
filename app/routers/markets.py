"""
Markets Router - Market data endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.services.market_service import get_market_service
from app.models.market import (
    MarketsResponse, MarketDetail, Orderbook
)

router = APIRouter()


@router.get("/markets", response_model=MarketsResponse)
async def list_markets(
    market_type: Optional[str] = Query(None, description="Filter by market type: spot or derivative")
):
    """
    List all available markets on Injective.
    
    Returns a summary of all spot and derivative markets including:
    - Market ID and ticker
    - Market type (spot/derivative)
    - Base and quote tokens
    - Current status
    
    **Query Parameters:**
    - `market_type`: Optional filter for "spot" or "derivative" markets
    """
    service = get_market_service()
    response = await service.get_all_markets()
    
    # Filter by market type if specified
    if market_type:
        filtered_markets = [m for m in response.markets if m.market_type == market_type]
        return MarketsResponse(
            markets=filtered_markets,
            total=len(filtered_markets),
            spot_count=len([m for m in filtered_markets if m.market_type == "spot"]),
            derivative_count=len([m for m in filtered_markets if m.market_type == "derivative"])
        )
    
    return response


@router.get("/markets/{market_id}", response_model=MarketDetail)
async def get_market(market_id: str):
    """
    Get detailed information for a specific market.
    
    Returns comprehensive market data including:
    - Market identification (ID, ticker, type)
    - Token information
    - Fee rates (maker/taker)
    - Tick sizes
    
    **Path Parameters:**
    - `market_id`: The unique Injective market identifier
    """
    service = get_market_service()
    market = await service.get_market(market_id)
    
    if not market:
        raise HTTPException(status_code=404, detail=f"Market {market_id} not found")
    
    return market


@router.get("/markets/{market_id}/orderbook", response_model=Orderbook)
async def get_orderbook(
    market_id: str,
    depth: int = Query(20, ge=1, le=50, description="Number of levels to return")
):
    """
    Get orderbook snapshot for a market.
    
    Returns the current orderbook state including:
    - Top bid and ask levels with quantities
    - Cumulative depth at each level
    - Best bid/ask spread and mid price
    
    **Path Parameters:**
    - `market_id`: The unique Injective market identifier
    
    **Query Parameters:**
    - `depth`: Number of price levels to return (1-50, default: 20)
    """
    service = get_market_service()
    orderbook = await service.get_orderbook(market_id)
    
    if not orderbook:
        raise HTTPException(status_code=404, detail=f"Orderbook for market {market_id} not found")
    
    # Limit depth
    orderbook.bids = orderbook.bids[:depth]
    orderbook.asks = orderbook.asks[:depth]
    
    return orderbook
