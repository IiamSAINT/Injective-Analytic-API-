"""
Tests for Ninja Analytics and Premium Features
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app

client = TestClient(app)

# Mock Data
MOCK_TRADES = [
    {"subaccountId": "inj1testaddress0000000000000000000000000000000", "price": "10", "quantity": "100", "executionSide": "buy"},
    {"subaccountId": "inj1whaleaddress0000000000000000000000000000000", "price": "10", "quantity": "50000", "executionSide": "buy"},
]

MOCK_MARKETS = [
    {"marketId": "0x123", "ticker": "INJ/USDT", "serviceProviderFee": "0.1", "marketType": "spot", "serviceProviderFee": "0.01"},
]

@pytest.fixture
def mock_client():
    with patch("app.services.ninja_service.get_injective_client") as mock:
        client_instance = AsyncMock()
        client_instance.get_spot_markets.return_value = MOCK_MARKETS
        client_instance.get_derivative_markets.return_value = []
        client_instance.get_spot_trades.return_value = MOCK_TRADES
        client_instance.get_derivative_trades.return_value = []
        mock.return_value = client_instance
        yield client_instance

def test_ninja_check_address():
    """Test checking a specific address."""
    addr = "inj1check"
    response = client.get(f"/api/v1/analytics/ninja/check/{addr}")
    assert response.status_code == 200
    data = response.json()
    assert data["address"] == addr

def test_premium_whales_no_auth():
    """Test accessing whales endpoint without API key."""
    response = client.get("/api/v1/premium/whales")
    assert response.status_code == 403

def test_premium_add_tag_auth():
    """Test adding a tag with auth."""
    headers = {"x-api-key": "secret_ninja_key"}
    payload = {"address": "inj1newwhale", "tag": "MegaWhale"}
    response = client.post("/api/v1/premium/tags", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["tag_added"] == "MegaWhale"
