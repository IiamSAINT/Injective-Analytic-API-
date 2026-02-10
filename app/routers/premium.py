from fastapi import APIRouter, Depends, Header, HTTPException, Body
from typing import List, Dict, Any
from app.models.ninja import NinjaTrader
from app.models.premium import WhaleResponse, TagRequest

from app.services.ninja_service import get_ninja_service, NinjaService
from app.utils.auth import verify_api_key

router = APIRouter(
    prefix="/premium",
    tags=["Premium Features"],
    dependencies=[Depends(verify_api_key)],
    responses={403: {"description": "Access Forbidden"}}
)

@router.get("/whales", response_model=WhaleResponse)
async def get_whale_activity(
    limit: int = 25,
    service: NinjaService = Depends(get_ninja_service)
):
    """
    [PREMIUM] Get a feed of high-value transactions (Whale Watch).
    Returns the most active addresses from recent blocks.
    """
    traders = await service.get_active_traders(limit=limit)
    whales = [t for t in traders if "Whale" in t.get("tags", []) or t.get("ninja_score", 0) >= 50]
    if not whales:
        whales = traders[:limit]
    return {"whales": whales[:limit]}

@router.post("/tags")
async def add_system_tag(
    request: TagRequest,
    service: NinjaService = Depends(get_ninja_service)
):
    """
    [PREMIUM] Admin endpoint to manually tag an address.
    """
    service.add_tag(request.address, request.tag)
    return {"status": "success", "address": request.address, "tag_added": request.tag}
