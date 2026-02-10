from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from app.models.ninja import NinjaTrader, AddressCheckResponse

from app.services.ninja_service import get_ninja_service, NinjaService

router = APIRouter(
    prefix="/analytics/ninja",
    tags=["Ninja Analytics"],
    responses={404: {"description": "Not found"}},
)

@router.get("/active", response_model=List[NinjaTrader])
async def get_active_traders(
    limit: int = 10,
    service: NinjaService = Depends(get_ninja_service)
):
    """
    Get top active traders across major markets based on recent activity.
    """
    return await service.get_active_traders(limit)

@router.get("/check/{address}", response_model=AddressCheckResponse)
async def check_address(
    address: str,
    service: NinjaService = Depends(get_ninja_service)
):
    """
    Check stats and tags for a specific address.
    """
    tags = service.get_tags(address)
    # in a real app, we'd fetch specific stats for this address too
    # for now, we return known tags
    return {
        "address": address,
        "tags": tags,
        "is_known_entity": len(tags) > 0
    }
