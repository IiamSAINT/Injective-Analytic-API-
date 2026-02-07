"""
Analytics Service - Business logic for computing market analytics
"""
from datetime import datetime, timezone
from typing import List, Optional
import statistics

from app.services.market_service import get_market_service
from app.models.analytics import (
    VolatilityMetrics, LiquidityMetrics, MarketHealthIndicator,
    MarketMover, TopMoversResponse, VolumeLeader, OverviewStats,
    AnalyticsOverview
)
from app.utils.cache import cached_analytics


class AnalyticsService:
    """Service for computing market analytics."""
    
    def __init__(self):
        self.market_service = get_market_service()
    
    @cached_analytics
    async def get_overview(self) -> AnalyticsOverview:
        """Get global market analytics overview."""
        markets_response = await self.market_service.get_all_markets()
        markets = markets_response.markets
        
        # Basic stats
        stats = OverviewStats(
            total_markets=len(markets),
            active_spot_markets=len([m for m in markets if m.market_type == "spot"]),
            active_derivative_markets=len([m for m in markets if m.market_type == "derivative"]),
            total_volume_24h=sum(m.volume_24h or 0 for m in markets),
            top_volume_market=None,
            average_spread_bps=0.0,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Top movers - based on price change
        sorted_by_change = sorted(
            [m for m in markets if m.price_change_24h is not None],
            key=lambda x: x.price_change_24h or 0,
            reverse=True
        )
        
        top_gainers = [
            MarketMover(
                market_id=m.market_id,
                ticker=m.ticker,
                price_change_24h=m.price_change_24h or 0,
                volume_24h=m.volume_24h or 0,
                last_price=m.last_price or 0
            )
            for m in sorted_by_change[:5] if (m.price_change_24h or 0) > 0
        ]
        
        top_losers = [
            MarketMover(
                market_id=m.market_id,
                ticker=m.ticker,
                price_change_24h=m.price_change_24h or 0,
                volume_24h=m.volume_24h or 0,
                last_price=m.last_price or 0
            )
            for m in reversed(sorted_by_change[-5:]) if (m.price_change_24h or 0) < 0
        ]
        
        # Volume leaders
        sorted_by_volume = sorted(
            [m for m in markets if m.volume_24h is not None],
            key=lambda x: x.volume_24h or 0,
            reverse=True
        )
        
        volume_leaders = [
            VolumeLeader(
                market_id=m.market_id,
                ticker=m.ticker,
                volume_24h=m.volume_24h or 0,
                volume_rank=i + 1
            )
            for i, m in enumerate(sorted_by_volume[:10])
        ]
        
        if volume_leaders:
            stats.top_volume_market = volume_leaders[0].ticker
        
        return AnalyticsOverview(
            stats=stats,
            top_gainers=top_gainers,
            top_losers=top_losers,
            volume_leaders=volume_leaders
        )
    
    @cached_analytics
    async def get_volatility(self, market_id: str) -> Optional[VolatilityMetrics]:
        """Calculate volatility metrics for a market."""
        market = await self.market_service.get_market(market_id)
        
        if not market:
            return None
        
        # Get orderbook and derive price info
        orderbook = await self.market_service.get_orderbook(market_id)
        
        if not orderbook or not orderbook.mid_price:
            # Return default metrics if no orderbook data
            return VolatilityMetrics(
                market_id=market_id,
                ticker=market.ticker,
                period="24h",
                volatility=0.0,
                volatility_percentage=0.0,
                high=market.high_24h or 0,
                low=market.low_24h or 0,
                range_percentage=0.0,
                average_price=orderbook.mid_price if orderbook else 0,
                calculated_at=datetime.now(timezone.utc)
            )
        
        # Calculate range-based volatility estimate
        high = market.high_24h or orderbook.mid_price * 1.02
        low = market.low_24h or orderbook.mid_price * 0.98
        avg_price = (high + low) / 2
        
        range_pct = ((high - low) / avg_price * 100) if avg_price > 0 else 0
        
        # Estimate volatility from range (Parkinson estimator approximation)
        volatility = (high - low) / (2 * 1.7)  # Simplified
        volatility_pct = (volatility / avg_price * 100) if avg_price > 0 else 0
        
        return VolatilityMetrics(
            market_id=market_id,
            ticker=market.ticker,
            period="24h",
            volatility=volatility,
            volatility_percentage=volatility_pct,
            high=high,
            low=low,
            range_percentage=range_pct,
            average_price=avg_price,
            calculated_at=datetime.now(timezone.utc)
        )
    
    @cached_analytics
    async def get_liquidity(self, market_id: str) -> Optional[LiquidityMetrics]:
        """Calculate liquidity metrics for a market."""
        market = await self.market_service.get_market(market_id)
        orderbook = await self.market_service.get_orderbook(market_id)
        
        if not market or not orderbook:
            return None
        
        # Calculate depth
        bid_depth = sum(level.quantity * level.price for level in orderbook.bids)
        ask_depth = sum(level.quantity * level.price for level in orderbook.asks)
        total_depth = bid_depth + ask_depth
        
        # Calculate spread in basis points
        spread = orderbook.spread or 0
        mid_price = orderbook.mid_price or 1
        spread_bps = (spread / mid_price * 10000) if mid_price > 0 else 10000
        
        # Depth ratio (bid/ask balance)
        depth_ratio = bid_depth / ask_depth if ask_depth > 0 else 0
        
        # Compute liquidity score (0-100)
        # Based on: depth, spread, and balance
        depth_score = min(100, (total_depth / 100000) * 100)  # Normalize by $100k
        spread_score = max(0, 100 - spread_bps)  # Lower spread = higher score
        balance_score = 100 - abs(depth_ratio - 1) * 50  # Closer to 1 = better
        
        liquidity_score = (depth_score * 0.4 + spread_score * 0.4 + balance_score * 0.2)
        liquidity_score = max(0, min(100, liquidity_score))
        
        return LiquidityMetrics(
            market_id=market_id,
            ticker=market.ticker,
            liquidity_score=round(liquidity_score, 2),
            bid_depth=round(bid_depth, 2),
            ask_depth=round(ask_depth, 2),
            total_depth=round(total_depth, 2),
            spread=spread,
            spread_bps=round(spread_bps, 2),
            depth_ratio=round(depth_ratio, 4),
            calculated_at=datetime.now(timezone.utc)
        )
    
    @cached_analytics
    async def get_market_health(self, market_id: str) -> Optional[MarketHealthIndicator]:
        """Calculate overall market health indicator."""
        volatility = await self.get_volatility(market_id)
        liquidity = await self.get_liquidity(market_id)
        
        if not volatility or not liquidity:
            return None
        
        # Health score components
        # Liquidity: higher is better (direct use)
        liquidity_component = liquidity.liquidity_score * 0.4
        
        # Volatility: moderate is best (too high or too low is bad)
        # Target volatility around 2-5% is healthy
        vol_pct = volatility.volatility_percentage
        if vol_pct < 0.5:
            vol_score = 50 + vol_pct * 100  # Low vol = okay but not great
        elif vol_pct <= 5:
            vol_score = 100 - abs(vol_pct - 2.5) * 10  # Sweet spot
        else:
            vol_score = max(0, 100 - (vol_pct - 5) * 10)  # High vol = bad
        volatility_component = vol_score * 0.3
        
        # Activity component (simplified - based on orderbook levels)
        activity_score = min(100, liquidity.total_depth / 1000 * 10)
        activity_component = activity_score * 0.3
        
        # Total health score
        health_score = liquidity_component + volatility_component + activity_component
        health_score = max(0, min(100, health_score))
        
        # Determine status
        if health_score >= 70:
            status = "healthy"
        elif health_score >= 40:
            status = "moderate"
        else:
            status = "weak"
        
        market = await self.market_service.get_market(market_id)
        
        return MarketHealthIndicator(
            market_id=market_id,
            ticker=market.ticker if market else "UNKNOWN",
            health_score=round(health_score, 2),
            liquidity_component=round(liquidity_component, 2),
            volatility_component=round(volatility_component, 2),
            activity_component=round(activity_component, 2),
            status=status,
            calculated_at=datetime.now(timezone.utc)
        )
    
    @cached_analytics
    async def get_top_movers(self, limit: int = 5) -> TopMoversResponse:
        """Get top gaining and losing markets."""
        overview = await self.get_overview()
        
        return TopMoversResponse(
            gainers=overview.top_gainers[:limit],
            losers=overview.top_losers[:limit],
            timestamp=datetime.now(timezone.utc)
        )


# Singleton instance
_service: Optional[AnalyticsService] = None


def get_analytics_service() -> AnalyticsService:
    """Get the analytics service singleton."""
    global _service
    if _service is None:
        _service = AnalyticsService()
    return _service
