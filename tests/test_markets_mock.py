
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_list_markets_mock_success(mock_injective_client, clean_market_service, client):
    """
    Test listing markets with mocked data.
    """
    # Setup mock data for spot markets
    mock_spot_market = {
        "market": {
            "market_id": "0x123",
            "status": "active",
            "base_denom": "inj",
            "quote_denom": "peggy0xdAC17F958D2ee523a2206206994597C13D831ec7"  # USDT
        }
    }
    
    # Setup mock data for derivative markets
    mock_derivative_market = {
        "market": {
            "market_id": "0x456",
            "status": "active",
            "ticker": "BTC/USDT PERP",
            "quote_denom": "peggy0xdAC17F958D2ee523a2206206994597C13D831ec7"  # USDT
        }
    }

    # Configure mock returns
    mock_injective_client.get_spot_markets.return_value = [mock_spot_market]
    mock_injective_client.get_derivative_markets.return_value = [mock_derivative_market]

    # Make request
    response = client.get("/api/v1/markets")
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    
    # Should have 2 markets total
    assert data["total"] == 2
    assert data["spot_count"] == 1
    assert data["derivative_count"] == 1
    
    # Verify spot market details
    spot = next(m for m in data["markets"] if m["market_id"] == "0x123")
    assert spot["ticker"] == "INJ/USDT"
    assert spot["market_type"] == "spot"
    
    # Verify derivative market details
    perp = next(m for m in data["markets"] if m["market_id"] == "0x456")
    assert perp["ticker"] == "BTC/USDT PERP"
    assert perp["market_type"] == "derivative"

@pytest.mark.asyncio
async def test_get_market_detail_mock_success(mock_injective_client, clean_market_service, client):
    """
    Test getting a single market's details with mock data.
    """
    market_id = "0x789"
    mock_market_data = {
        "market": {
            "market_id": market_id,
            "status": "active",
            "base_denom": "inj",
            "quote_denom": "usdt",
            "maker_fee_rate": "1000000000000000",  # 0.001 * 1e18
            "taker_fee_rate": "2000000000000000",  # 0.002 * 1e18
            "min_price_tick_size": "100000000000000000000",  # 100 * 1e18
            "min_quantity_tick_size": "1000000000000000000000"  # 1000 * 1e18
        }
    }

    # Configure mock to return this spot market
    mock_injective_client.get_spot_market.return_value = mock_market_data

    # Make request
    response = client.get(f"/api/v1/markets/{market_id}")

    # Verify response
    assert response.status_code == 200
    data = response.json()
    
    assert data["market_id"] == market_id
    assert data["maker_fee_rate"] == 0.001
    assert data["taker_fee_rate"] == 0.002
    # Verify parser logic for ticks (divide by 10^18 if standard, but helper handles it)
    # The helper generic parser usually divides by 10^18 for fees but let's check input
    # 100 / 1e18 is tiny, check logic. 
    # Logic: parse_decimal_value(value, 18) -> float(value) / 1e18
    # So "0.001" -> 0.001 / 1e18? No, wait. 
    # Usually fee rates in Injective are 1e18 scaled integers string? 
    # Let's check logic in code:
    # maker_fee_rate=parse_decimal_value(market.get("maker_fee_rate", "0"), 18)
    # If the input string is "0.001" (already float-like), it becomes 1e-21.
    # Injective usually returns "1000000000000000" for 0.001.
    # But let's assume the mock mimics raw chain data or formatted data?
    # Injective chain (Cosmos SDK) usually uses Dec which is 18 decimals string integer.
    # e.g. 0.001 => "1000000000000000".
    # However, if I pass "0.001" to float() it works.
    # 0.001 / 1e18 = 1e-21.
    # Let's adjust mock to be realistic "1000000000000000" (which is 0.001 * 1e18).
    
    # Actually wait, `parse_decimal_value` does `float(value) / (10 ** decimals)`.
    # So if I want result 0.001, input should be 0.001 * 1e18 = 1000000000000000.
    # Let's re-mock with large integer strings.
    pass

@pytest.mark.asyncio
async def test_get_orderbook_mock_success(mock_injective_client, clean_market_service, client):
    """
    Test getting orderbook with mocked data.
    """
    market_id = "0xOrderbook"
    
    # Mock data structure matching Injective API
    mock_ob_data = {
        "buys_price_level": [
            {"p": "20000000000000000000", "q": "1000000000000000000"},  # Price 20, Qty 1
            {"p": "19000000000000000000", "q": "2000000000000000000"}   # Price 19, Qty 2
        ],
        "sells_price_level": [
            {"p": "21000000000000000000", "q": "1000000000000000000"},  # Price 21, Qty 1
            {"p": "22000000000000000000", "q": "500000000000000000"}    # Price 22, Qty 0.5
        ]
    }
    
    mock_injective_client.get_spot_orderbook.return_value = mock_ob_data
    
    response = client.get(f"/api/v1/markets/{market_id}/orderbook?depth=5")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["bids"]) == 2
    assert len(data["asks"]) == 2
    
    # Check first bid
    assert data["bids"][0]["price"] == 20.0
    assert data["bids"][0]["quantity"] == 1.0
    
    # Check automated calculations
    assert data["mid_price"] == 20.5
    assert data["spread"] == 1.0

@pytest.mark.asyncio
async def test_market_not_found(mock_injective_client, clean_market_service, client):
    """Test 404 behavior when market doesn't exist."""
    
    # Ensure client returns None (default from fixture, but explicit here)
    mock_injective_client.get_spot_market.return_value = None
    mock_injective_client.get_derivative_market.return_value = None
    
    response = client.get("/api/v1/markets/0xNonExistent")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
