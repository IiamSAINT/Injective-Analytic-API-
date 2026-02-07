"""
Injective API Client - Wrapper for Injective public APIs
"""
import httpx
from typing import Any, Dict, List, Optional
from datetime import datetime

from app.config import get_settings

settings = get_settings()


class InjectiveClient:
    """Client for interacting with Injective public APIs."""
    
    def __init__(self):
        self.lcd_url = settings.injective_lcd_url
        self.timeout = httpx.Timeout(30.0)
    
    async def _get(self, url: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a GET request to Injective API."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    
    async def get_spot_markets(self) -> List[Dict[str, Any]]:
        """Fetch all spot markets from Injective."""
        url = f"{self.lcd_url}/injective/exchange/v1beta1/spot/markets"
        try:
            data = await self._get(url)
            return data.get("markets", [])
        except Exception as e:
            print(f"Error fetching spot markets: {e}")
            return []
    
    async def get_derivative_markets(self) -> List[Dict[str, Any]]:
        """Fetch all derivative markets from Injective."""
        url = f"{self.lcd_url}/injective/exchange/v1beta1/derivative/markets"
        try:
            data = await self._get(url)
            return data.get("markets", [])
        except Exception as e:
            print(f"Error fetching derivative markets: {e}")
            return []
    
    async def get_spot_market(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific spot market."""
        url = f"{self.lcd_url}/injective/exchange/v1beta1/spot/markets/{market_id}"
        try:
            data = await self._get(url)
            return data.get("market")
        except Exception as e:
            print(f"Error fetching spot market {market_id}: {e}")
            return None
    
    async def get_derivative_market(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific derivative market."""
        url = f"{self.lcd_url}/injective/exchange/v1beta1/derivative/markets/{market_id}"
        try:
            data = await self._get(url)
            return data.get("market")
        except Exception as e:
            print(f"Error fetching derivative market {market_id}: {e}")
            return None
    
    async def get_spot_orderbook(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Fetch orderbook for a spot market."""
        url = f"{self.lcd_url}/injective/exchange/v1beta1/spot/orderbook/{market_id}"
        try:
            data = await self._get(url)
            return data
        except Exception as e:
            print(f"Error fetching spot orderbook for {market_id}: {e}")
            return None
    
    async def get_derivative_orderbook(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Fetch orderbook for a derivative market."""
        url = f"{self.lcd_url}/injective/exchange/v1beta1/derivative/orderbook/{market_id}"
        try:
            data = await self._get(url)
            return data
        except Exception as e:
            print(f"Error fetching derivative orderbook for {market_id}: {e}")
            return None
    
    async def get_oracle_prices(self) -> List[Dict[str, Any]]:
        """Fetch oracle price feeds."""
        url = f"{self.lcd_url}/injective/oracle/v1beta1/price_feeds"
        try:
            data = await self._get(url)
            return data.get("price_feeds", [])
        except Exception as e:
            print(f"Error fetching oracle prices: {e}")
            return []
    
    async def health_check(self) -> bool:
        """Check if Injective API is reachable."""
        try:
            url = f"{self.lcd_url}/cosmos/base/tendermint/v1beta1/syncing"
            await self._get(url)
            return True
        except Exception:
            return False


# Singleton instance
_client: Optional[InjectiveClient] = None


def get_injective_client() -> InjectiveClient:
    """Get the Injective client singleton."""
    global _client
    if _client is None:
        _client = InjectiveClient()
    return _client
