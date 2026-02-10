"""
Injective API Client - Wrapper for Injective public APIs
"""
import logging
import httpx
from typing import Any, Dict, List, Optional
from datetime import datetime

from app.config import get_settings

logger = logging.getLogger(__name__)
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
            logger.error("Failed to fetch spot markets: %s", e)
            return []
    
    async def get_derivative_markets(self) -> List[Dict[str, Any]]:
        """Fetch all derivative markets from Injective."""
        url = f"{self.lcd_url}/injective/exchange/v1beta1/derivative/markets"
        try:
            data = await self._get(url)
            return data.get("markets", [])
        except Exception as e:
            logger.error("Failed to fetch derivative markets: %s", e)
            return []
    
    async def get_spot_market(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific spot market."""
        url = f"{self.lcd_url}/injective/exchange/v1beta1/spot/markets/{market_id}"
        try:
            data = await self._get(url)
            return data.get("market")
        except Exception as e:
            logger.warning("Failed to fetch spot market %s: %s", market_id, e)
            return None
    
    async def get_derivative_market(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific derivative market."""
        url = f"{self.lcd_url}/injective/exchange/v1beta1/derivative/markets/{market_id}"
        try:
            data = await self._get(url)
            return data.get("market")
        except Exception as e:
            logger.warning("Failed to fetch derivative market %s: %s", market_id, e)
            return None
    
    async def get_spot_orderbook(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Fetch orderbook for a spot market."""
        url = f"{self.lcd_url}/injective/exchange/v1beta1/spot/orderbook/{market_id}"
        try:
            data = await self._get(url)
            return data
        except Exception as e:
            logger.warning("Failed to fetch spot orderbook for %s: %s", market_id, e)
            return None
    
    async def get_derivative_orderbook(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Fetch orderbook for a derivative market."""
        url = f"{self.lcd_url}/injective/exchange/v1beta1/derivative/orderbook/{market_id}"
        try:
            data = await self._get(url)
            return data
        except Exception as e:
            logger.warning("Failed to fetch derivative orderbook for %s: %s", market_id, e)
            return None
    
    async def get_spot_trades(self, market_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch recent trades for a spot market."""
        url = f"{self.lcd_url}/injective/exchange/v1beta1/spot/trades"
        params = {"market_id": market_id, "limit": limit}
        try:
            data = await self._get(url, params=params)
            return data.get("trades", [])
        except Exception as e:
            logger.warning("Failed to fetch spot trades for %s: %s", market_id, e)
            return []
            
    async def get_derivative_trades(self, market_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch recent trades for a derivative market."""
        url = f"{self.lcd_url}/injective/exchange/v1beta1/derivative/trades"
        params = {"market_id": market_id, "limit": limit}
        try:
            data = await self._get(url, params=params)
            return data.get("trades", [])
        except Exception as e:
            logger.warning("Failed to fetch derivative trades for %s: %s", market_id, e)
            return []
    
    async def get_oracle_prices(self) -> List[Dict[str, Any]]:
        """Fetch oracle price feeds."""
        url = f"{self.lcd_url}/injective/oracle/v1beta1/price_feeds"
        try:
            data = await self._get(url)
            return data.get("price_feeds", [])
        except Exception as e:
            logger.error("Failed to fetch oracle prices: %s", e)
            return []
    
    async def health_check(self) -> bool:
        """Check if Injective API is reachable."""
        try:
            url = f"{self.lcd_url}/cosmos/base/tendermint/v1beta1/syncing"
            await self._get(url)
            return True
        except Exception:
            return False

    async def get_latest_block(self) -> Dict[str, Any]:
        """Fetch the latest block to get current height."""
        url = f"{self.lcd_url}/cosmos/base/tendermint/v1beta1/blocks/latest"
        try:
            data = await self._get(url)
            return data.get("block", {})
        except Exception as e:
            logger.error("Failed to fetch latest block: %s", e)
            return {}

    async def get_block_txs(self, height: int) -> List[Dict[str, Any]]:
        """Fetch decoded transactions for a specific block height."""
        url = f"{self.lcd_url}/cosmos/tx/v1beta1/txs/block/{height}"
        try:
            data = await self._get(url)
            return data.get("txs", [])
        except Exception as e:
            logger.warning("Failed to fetch txs for block %d: %s", height, e)
            return []

    async def get_total_supply(self) -> Dict[str, Any]:
        """Fetch total supply of INJ."""
        url = f"{self.lcd_url}/cosmos/bank/v1beta1/supply/by_denom"
        try:
            data = await self._get(url, params={"denom": "inj"})
            return data
        except Exception as e:
            logger.error("Failed to fetch total supply: %s", e)
            return {}

    async def get_staking_pool(self) -> Dict[str, Any]:
        """Fetch staking pool (bonded tokens)."""
        url = f"{self.lcd_url}/cosmos/staking/v1beta1/pool"
        try:
            data = await self._get(url)
            return data.get("pool", {})
        except Exception as e:
            logger.error("Failed to fetch staking pool: %s", e)
            return {}

    async def get_mint_params(self) -> Dict[str, Any]:
        """Fetch minting parameters."""
        url = f"{self.lcd_url}/cosmos/mint/v1beta1/params"
        try:
            data = await self._get(url)
            return data.get("params", {})
        except Exception as e:
            logger.error("Failed to fetch mint params: %s", e)
            return {}

    async def get_inflation(self) -> Dict[str, Any]:
        """Fetch current inflation rate."""
        url = f"{self.lcd_url}/cosmos/mint/v1beta1/inflation"
        try:
            data = await self._get(url)
            return data
        except Exception as e:
            logger.error("Failed to fetch inflation: %s", e)
            return {}

    async def get_annual_provisions(self) -> Dict[str, Any]:
        """Fetch annual provisions (minted tokens)."""
        url = f"{self.lcd_url}/cosmos/mint/v1beta1/annual_provisions"
        try:
            data = await self._get(url)
            return data
        except Exception as e:
            logger.error("Failed to fetch annual provisions: %s", e)
            return {}

    async def get_balance(self, address: str, denom: str = "inj") -> float:
        """Fetch balance of an address."""
        url = f"{self.lcd_url}/cosmos/bank/v1beta1/balances/{address}/by_denom?denom={denom}"
        try:
            data = await self._get(url) 
            amount_str = data.get("balance", {}).get("amount", "0")
            return float(amount_str) 
        except Exception as e:
            logger.warning("Failed to fetch balance for %s: %s", address, e)
            return 0.0


# Singleton instance
_client: Optional[InjectiveClient] = None


def get_injective_client() -> InjectiveClient:
    """Get the Injective client singleton."""
    global _client
    if _client is None:
        _client = InjectiveClient()
    return _client
