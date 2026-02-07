"""
Market Service - Business logic for market data processing
"""
from datetime import datetime, timezone
from typing import List, Optional, Tuple
import re

from app.services.injective_client import get_injective_client
from app.models.market import (
    MarketSummary, MarketDetail, Orderbook, OrderbookLevel,
    MarketsResponse
)
from app.utils.cache import cached_market


def parse_denom_to_symbol(denom: str) -> str:
    """Parse a denom string to extract the token symbol."""
    if not denom:
        return "UNKNOWN"
    
    # Handle factory tokens: factory/inj.../token
    if denom.startswith("factory/"):
        parts = denom.split("/")
        if len(parts) >= 3:
            return parts[-1].upper()
    
    # Handle IBC tokens
    if denom.startswith("ibc/"):
        return denom[:10].upper() + "..."
    
    # Handle peggy tokens: peggy0x...
    if denom.startswith("peggy"):
        # Common known tokens
        known_peggy = {
            "peggy0xdAC17F958D2ee523a2206206994597C13D831ec7": "USDT",
            "peggy0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48": "USDC",
            "peggy0x111111111117dC0aa78b770fA6A738034120C302": "1INCH",
        }
        if denom in known_peggy:
            return known_peggy[denom]
        return "PEGGY"
    
    # Handle native INJ
    if denom == "inj":
        return "INJ"
    
    # Default: return first 6 chars uppercase
    return denom[:6].upper()


def extract_ticker(base_denom: str, quote_denom: str) -> str:
    """Create a ticker from base and quote denoms."""
    base = parse_denom_to_symbol(base_denom)
    quote = parse_denom_to_symbol(quote_denom)
    return f"{base}/{quote}"


def parse_decimal_value(value: str, decimals: int = 18) -> float:
    """Parse a string decimal value with given decimals."""
    if not value:
        return 0.0
    try:
        return float(value) / (10 ** decimals)
    except (ValueError, TypeError):
        return 0.0


class MarketService:
    """Service for processing market data."""
    
    def __init__(self):
        self.client = get_injective_client()
    
    @cached_market
    async def get_all_markets(self) -> MarketsResponse:
        """Get all markets (spot and derivative) with summaries."""
        spot_markets = await self.client.get_spot_markets()
        derivative_markets = await self.client.get_derivative_markets()
        
        markets: List[MarketSummary] = []
        
        # Process spot markets
        for market in spot_markets:
            try:
                market_data = market.get("market", market)
                base_denom = market_data.get("base_denom", "")
                quote_denom = market_data.get("quote_denom", "")
                
                summary = MarketSummary(
                    market_id=market_data.get("market_id", ""),
                    ticker=extract_ticker(base_denom, quote_denom),
                    market_type="spot",
                    base_token=parse_denom_to_symbol(base_denom),
                    quote_token=parse_denom_to_symbol(quote_denom),
                    status=market_data.get("status", "active")
                )
                markets.append(summary)
            except Exception as e:
                print(f"Error processing spot market: {e}")
                continue
        
        # Process derivative markets
        for market in derivative_markets:
            try:
                market_data = market.get("market", market)
                perp_info = market_data.get("perpetual_market_info", {})
                ticker = market_data.get("ticker", "UNKNOWN/USDT")
                quote_denom = market_data.get("quote_denom", "")
                
                # Extract base from ticker if available
                base_token = ticker.split("/")[0] if "/" in ticker else ticker.replace("-PERP", "")
                
                summary = MarketSummary(
                    market_id=market_data.get("market_id", ""),
                    ticker=ticker,
                    market_type="derivative",
                    base_token=base_token,
                    quote_token=parse_denom_to_symbol(quote_denom),
                    status=market_data.get("status", "active")
                )
                markets.append(summary)
            except Exception as e:
                print(f"Error processing derivative market: {e}")
                continue
        
        return MarketsResponse(
            markets=markets,
            total=len(markets),
            spot_count=len([m for m in markets if m.market_type == "spot"]),
            derivative_count=len([m for m in markets if m.market_type == "derivative"])
        )
    
    @cached_market
    async def get_market(self, market_id: str) -> Optional[MarketDetail]:
        """Get detailed information for a specific market."""
        # Try spot first
        market_data = await self.client.get_spot_market(market_id)
        market_type = "spot"
        
        if not market_data:
            # Try derivative
            market_data = await self.client.get_derivative_market(market_id)
            market_type = "derivative"
        
        if not market_data:
            return None
        
        market = market_data.get("market", market_data)
        
        if market_type == "spot":
            base_denom = market.get("base_denom", "")
            quote_denom = market.get("quote_denom", "")
            ticker = extract_ticker(base_denom, quote_denom)
            base_token = parse_denom_to_symbol(base_denom)
        else:
            ticker = market.get("ticker", "UNKNOWN")
            base_token = ticker.split("/")[0] if "/" in ticker else ticker
            quote_denom = market.get("quote_denom", "")
        
        return MarketDetail(
            market_id=market.get("market_id", market_id),
            ticker=ticker,
            market_type=market_type,
            base_token=base_token,
            quote_token=parse_denom_to_symbol(market.get("quote_denom", "")),
            status=market.get("status", "active"),
            maker_fee_rate=parse_decimal_value(market.get("maker_fee_rate", "0"), 18),
            taker_fee_rate=parse_decimal_value(market.get("taker_fee_rate", "0"), 18),
            min_price_tick_size=parse_decimal_value(market.get("min_price_tick_size", "0"), 18),
            min_quantity_tick_size=parse_decimal_value(market.get("min_quantity_tick_size", "0"), 18)
        )
    
    @cached_market
    async def get_orderbook(self, market_id: str) -> Optional[Orderbook]:
        """Get orderbook for a market."""
        # Try spot first
        ob_data = await self.client.get_spot_orderbook(market_id)
        
        if not ob_data or not ob_data.get("buys_price_level") and not ob_data.get("sells_price_level"):
            # Try derivative
            ob_data = await self.client.get_derivative_orderbook(market_id)
        
        if not ob_data:
            return None
        
        bids: List[OrderbookLevel] = []
        asks: List[OrderbookLevel] = []
        
        # Process bids
        cumulative = 0.0
        for level in ob_data.get("buys_price_level", []):
            price = parse_decimal_value(level.get("p", "0"), 18)
            quantity = parse_decimal_value(level.get("q", "0"), 18)
            cumulative += quantity
            bids.append(OrderbookLevel(price=price, quantity=quantity, total=cumulative))
        
        # Process asks
        cumulative = 0.0
        for level in ob_data.get("sells_price_level", []):
            price = parse_decimal_value(level.get("p", "0"), 18)
            quantity = parse_decimal_value(level.get("q", "0"), 18)
            cumulative += quantity
            asks.append(OrderbookLevel(price=price, quantity=quantity, total=cumulative))
        
        # Calculate spread
        best_bid = bids[0].price if bids else 0
        best_ask = asks[0].price if asks else 0
        spread = best_ask - best_bid if best_bid and best_ask else None
        mid_price = (best_bid + best_ask) / 2 if best_bid and best_ask else None
        spread_percentage = (spread / mid_price * 100) if spread and mid_price else None
        
        return Orderbook(
            market_id=market_id,
            timestamp=datetime.now(timezone.utc),
            bids=bids[:20],  # Limit to top 20 levels
            asks=asks[:20],
            spread=spread,
            spread_percentage=spread_percentage,
            mid_price=mid_price
        )


# Singleton instance
_service: Optional[MarketService] = None


def get_market_service() -> MarketService:
    """Get the market service singleton."""
    global _service
    if _service is None:
        _service = MarketService()
    return _service
