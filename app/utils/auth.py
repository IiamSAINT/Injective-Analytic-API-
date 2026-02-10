from fastapi import Header, HTTPException, status
import os
from typing import Optional

# Simple API Key Auth
# In production, use a database of keys or a proper auth provider
CORRECT_API_KEY = os.getenv("PREMIUM_API_KEY", "secret_ninja_key")

async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """
    Verify the x-api-key header for premium endpoints.
    """
    if x_api_key != CORRECT_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API Key for Premium Access"
        )
    return x_api_key
