"""
Tests for Analytics Endpoints
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.main import app
from app.models.market import MarketSummary, MarketDetail, Orderbook, OrderbookLevel, MarketsResponse
from app.services.analytics_service import get_analytics_service, AnalyticsService
from fastapi.testclient import TestClient

client = TestClient(app)

# Sample data for mocks
MOCK_TIMESTAMP = datetime(2025, 1, 1, 12, 0, 0)

MOCK_MARKET_SUMMARY_SPOT = MarketSummary(
    market_id="spot_market_1",
    ticker="INJ/USDT",
    market_type="spot",
    base_token="INJ",
    quote_token="USDT",
    status="active",
    price_change_24h=5.0,
    volume_24h=1000000.0,
    last_price=25.0,
    high_24h=26.0,
    low_24h=24.0
)

MOCK_MARKET_SUMMARY_DERIVATIVE = MarketSummary(
    market_id="deriv_market_1",
    ticker="BTC/USDT-PERP",
    market_type="derivative",
    base_token="BTC",
    quote_token="USDT",
    status="active",
    price_change_24h=-2.0,
    volume_24h=5000000.0,
    last_price=50000.0
)

MOCK_MARKET_DETAIL = MarketDetail(
    market_id="spot_market_1",
    ticker="INJ/USDT",
    market_type="spot",
    base_token="INJ",
    quote_token="USDT",
    status="active",
    maker_fee_rate=0.001,
    taker_fee_rate=0.002,
    price_change_24h=5.0,
    volume_24h=1000000.0,
    high_24h=26.0,
    low_24h=24.0,
    last_price=25.0
)

MOCK_ORDERBOOK = Orderbook(
    market_id="spot_market_1",
    timestamp=MOCK_TIMESTAMP,
    bids=[
        OrderbookLevel(price=24.9, quantity=100.0, total=100.0),
        OrderbookLevel(price=24.8, quantity=200.0, total=300.0)
    ],
    asks=[
        OrderbookLevel(price=25.1, quantity=100.0, total=100.0),
        OrderbookLevel(price=25.2, quantity=200.0, total=300.0)
    ],
    spread=0.2,
    spread_percentage=0.8,
    mid_price=25.0
)


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singletons to ensure fresh service instances for each test."""
    import app.services.analytics_service
    app.services.analytics_service._service = None
    yield
    app.services.analytics_service._service = None


@pytest.fixture
def mock_market_service():
    with patch("app.services.analytics_service.get_market_service") as mock_get:
        service_mock = AsyncMock()
        mock_get.return_value = service_mock
        
        # Setup common returns
        service_mock.get_all_markets.return_value = MarketsResponse(
            markets=[MOCK_MARKET_SUMMARY_SPOT, MOCK_MARKET_SUMMARY_DERIVATIVE],
            total=2,
            spot_count=1,
            derivative_count=1
        )
        service_mock.get_market.return_value = MOCK_MARKET_DETAIL
        service_mock.get_orderbook.return_value = MOCK_ORDERBOOK
        
        yield service_mock


@pytest.fixture
def clear_cache():
    # Clear cache before each test to ensure fresh mocks are used
    from app.utils.cache import clear_all_caches
    clear_all_caches()
    yield
    clear_all_caches()


@pytest.mark.asyncio
async def test_analytics_overview(mock_market_service, clear_cache):
    """Test the analytics overview endpoint."""
    response = client.get("/api/v1/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    
    # Check stats
    stats = data["stats"]
    assert stats["total_markets"] == 2
    assert stats["active_spot_markets"] == 1
    assert stats["active_derivative_markets"] == 1
    assert stats["total_volume_24h"] == 6000000.0
    
    # Check gainers/losers
    gainers = data["top_gainers"]
    losers = data["top_losers"]
    assert len(gainers) == 1
    assert gainers[0]["ticker"] == "INJ/USDT"
    assert len(losers) == 1
    assert losers[0]["ticker"] == "BTC/USDT-PERP"


@pytest.mark.asyncio
async def test_top_movers(mock_market_service, clear_cache):
    """Test the top movers endpoint."""
    response = client.get("/api/v1/analytics/top-movers?limit=5")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["gainers"]) == 1
    assert data["gainers"][0]["ticker"] == "INJ/USDT"
    assert len(data["losers"]) == 1
    assert data["losers"][0]["ticker"] == "BTC/USDT-PERP"


@pytest.mark.asyncio
async def test_volatility(mock_market_service, clear_cache):
    """Test the volatility endpoint."""
    response = client.get("/api/v1/analytics/spot_market_1/volatility")
    assert response.status_code == 200
    data = response.json()
    
    assert data["market_id"] == "spot_market_1"
    assert data["ticker"] == "INJ/USDT"
    assert data["period"] == "24h"
    # Logic verification: high=26, low=24, avg=25. Range=2.0. Vol estimate ~ 2.0 / 3.4
    assert data["high"] == 26.0
    assert data["low"] == 24.0
    assert data["average_price"] == 25.0


@pytest.mark.asyncio
async def test_liquidity(mock_market_service, clear_cache):
    """Test the liquidity endpoint."""
    response = client.get("/api/v1/analytics/spot_market_1/liquidity")
    assert response.status_code == 200
    data = response.json()
    
    assert data["market_id"] == "spot_market_1"
    # Bid depth: 24.9*100 + 24.8*200 = 2490 + 4960 = 7450
    # Ask depth: 25.1*100 + 25.2*200 = 2510 + 5040 = 7550
    assert data["bid_depth"] == 7450.0
    assert data["ask_depth"] == 7550.0
    assert data["spread"] == 0.2


@pytest.mark.asyncio
async def test_market_health(mock_market_service, clear_cache):
    """Test the market health endpoint."""
    response = client.get("/api/v1/analytics/spot_market_1/health")
    assert response.status_code == 200
    data = response.json()
    
    assert data["market_id"] == "spot_market_1"
    assert "health_score" in data
    assert "liquidity_component" in data
    assert "volatility_component" in data
    assert "activity_component" in data
    assert data["status"] in ["healthy", "moderate", "weak"]


@pytest.mark.asyncio
async def test_market_not_found(mock_market_service, clear_cache):
    """Test 404 for non-existent market."""
    mock_market_service.get_market.return_value = None
    
    response = client.get("/api/v1/analytics/invalid_id/volatility")
    assert response.status_code == 404

