"""
Tests for Health Endpoints
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test suite for health check endpoints."""
    
    def test_health_check(self):
        """Test basic health check returns 200."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
    
    def test_detailed_health(self):
        """Test detailed health check includes cache stats."""
        response = client.get("/api/v1/health/detailed")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "cache" in data
        assert "market_cache" in data["cache"]
        assert "analytics_cache" in data["cache"]
    
    def test_root_endpoint(self):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data


class TestInjectiveConnectivity:
    """Test Injective network connectivity."""
    
    def test_injective_health_check(self):
        """Test Injective connectivity check endpoint."""
        response = client.get("/api/v1/health/injective")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "connected" in data
        assert "endpoint" in data
        assert "timestamp" in data
