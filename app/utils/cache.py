"""
Caching utilities using cachetools
"""
from functools import wraps
from typing import Any, Callable, Optional
from cachetools import TTLCache
import hashlib
import json

# Global cache instances
_market_cache: TTLCache = TTLCache(maxsize=100, ttl=10)
_analytics_cache: TTLCache = TTLCache(maxsize=100, ttl=30)


def get_cache_key(*args, **kwargs) -> str:
    """Generate a cache key from function arguments."""
    key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
    return hashlib.md5(key_data.encode()).hexdigest()


def cached_market(func: Callable) -> Callable:
    """Decorator to cache market data with short TTL."""
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        key = f"{func.__name__}:{get_cache_key(*args, **kwargs)}"
        
        if key in _market_cache:
            return _market_cache[key]
        
        result = await func(*args, **kwargs)
        _market_cache[key] = result
        return result
    
    return wrapper


def cached_analytics(func: Callable) -> Callable:
    """Decorator to cache analytics data with longer TTL."""
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        key = f"{func.__name__}:{get_cache_key(*args, **kwargs)}"
        
        if key in _analytics_cache:
            return _analytics_cache[key]
        
        result = await func(*args, **kwargs)
        _analytics_cache[key] = result
        return result
    
    return wrapper


def clear_market_cache():
    """Clear the market cache."""
    _market_cache.clear()


def clear_analytics_cache():
    """Clear the analytics cache."""
    _analytics_cache.clear()


def clear_all_caches():
    """Clear all caches."""
    clear_market_cache()
    clear_analytics_cache()


def get_cache_stats() -> dict:
    """Get cache statistics."""
    return {
        "market_cache": {
            "size": len(_market_cache),
            "maxsize": _market_cache.maxsize,
            "ttl": _market_cache.ttl
        },
        "analytics_cache": {
            "size": len(_analytics_cache),
            "maxsize": _analytics_cache.maxsize,
            "ttl": _analytics_cache.ttl
        }
    }
