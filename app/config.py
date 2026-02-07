"""
Injective Market Intelligence API - Configuration
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Info
    api_title: str = "Injective Market Intelligence API"
    api_description: str = "A developer-focused REST API for Injective market data and analytics"
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
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
