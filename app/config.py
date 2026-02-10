"""
Injective Market & Network Data API - Configuration
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Info
    api_title: str = "Injective Market & Network Data API"
    api_description: str = "REST API for Injective Protocol market data, analytics, and network economics"
    api_version: str = "1.0.0"
    debug: bool = True
    
    # Injective Network Endpoints (Mainnet)
    injective_lcd_url: str = "https://sentry.lcd.injective.network:443"
    injective_exchange_api_url: str = "https://sentry.exchange.grpc-web.injective.network:443"
    
    # Alternative REST endpoints for exchange data
    injective_indexer_url: str = "https://sentry.exchange.grpc-web.injective.network"
    
    # Cache TTL (seconds)
    market_cache_ttl: int = 10
    analytics_cache_ttl: int = 30
    
    # Supply Constants
    inj_initial_supply: float = 100_000_000
    inj_decimals: int = 18
    inj_burn_address: str = "inj1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqe2hm49"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
