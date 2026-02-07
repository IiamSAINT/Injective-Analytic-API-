"""
Tests for Markets Endpoints
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestMarketsEndpoints:
    """Test suite for market endpoints."""
    
    def test_list_markets(self):
        """Test listing all markets returns expected structure."""
        response = client.get("/api/v1/markets")
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "markets" in data
        assert "total" in data
        assert "spot_count" in data
        assert "derivative_count" in data
        assert isinstance(data["markets"], list)
    
    def test_list_markets_filter_spot(self):
        """Test filtering markets by type=spot."""
        response = client.get("/api/v1/markets", params={"market_type": "spot"})
        assert response.status_code == 200
        data = response.json()
        
        # All returned markets should be spot
        for market in data["markets"]:
            assert market["market_type"] == "spot"
    
    def test_list_markets_filter_derivative(self):
        """Test filtering markets by type=derivative."""
        response = client.get("/api/v1/markets", params={"market_type": "derivative"})
        assert response.status_code == 200
        data = response.json()
        
        # All returned markets should be derivative
        for market in data["markets"]:
            assert market["market_type"] == "derivative"
    
    def test_get_market_not_found(self):
        """Test getting a non-existent market returns 404."""
        response = client.get("/api/v1/markets/invalid_market_id_12345")
        assert response.status_code == 404
    
    def test_orderbook_not_found(self):
        """Test getting orderbook for non-existent market returns 404."""
        response = client.get("/api/v1/markets/invalid_market_id_12345/orderbook")
        assert response.status_code == 404


class TestMarketDetails:
    """Test market detail endpoints with real data."""
    
    def test_market_summary_fields(self):
        """Test that market summaries have required fields."""
        response = client.get("/api/v1/markets")
        assert response.status_code == 200
        data = response.json()
        
        if data["markets"]:
            market = data["markets"][0]
            assert "market_id" in market
            assert "ticker" in market
            assert "market_type" in market
            assert "base_token" in market
            assert "quote_token" in market
