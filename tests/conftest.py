
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.injective_client import InjectiveClient
from app.services.market_service import MarketService, get_market_service
import app.services.market_service as service_module
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def mock_injective_client(monkeypatch):
    """
    Fixture that mocks the InjectiveClient singleton using monkeypatch.
    """
    # Create a mock instance
    mock_client = AsyncMock(spec=InjectiveClient)
    
    # Mock methods to return empty/safe defaults by default
    mock_client.get_spot_markets.return_value = []
    mock_client.get_derivative_markets.return_value = []
    mock_client.get_spot_market.return_value = None
    mock_client.get_derivative_market.return_value = None
    mock_client.get_spot_orderbook.return_value = None
    mock_client.get_derivative_orderbook.return_value = None
    mock_client.health_check.return_value = True

    # Patch the singleton getter in injective_client
    monkeypatch.setattr('app.services.injective_client.get_injective_client', lambda: mock_client)
    
    # Also patch the global _client variable just in case
    monkeypatch.setattr('app.services.injective_client._client', mock_client)

    return mock_client

@pytest.fixture
def clean_market_service():
    """
    Fixture to reset the MarketService singleton before and after tests.
    This ensures that a fresh service instance (using the mocked client) is created.
    """
    # Reset singleton
    service_module._service = None
    yield
    service_module._service = None

@pytest.fixture
def client():
    return TestClient(app)
