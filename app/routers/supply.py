from fastapi import APIRouter, Depends, HTTPException
from app.services.supply_service import SupplyService, get_supply_service
from app.models.supply import SupplyOverview, InflationMetrics

router = APIRouter(
    prefix="/analytics/supply",
    tags=["Supply & Economics"]
)

@router.get("/overview", response_model=SupplyOverview)
async def get_supply_overview(
    service: SupplyService = Depends(get_supply_service)
):
    """
    Get complete supply overview including Total Supply, Staked, and Burned amounts.
    """
    try:
        data = await service.get_overview()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/inflation", response_model=InflationMetrics)
async def get_inflation_metrics(
    service: SupplyService = Depends(get_supply_service)
):
    """
    Get detailed inflation and minting parameters.
    """
    try:
        data = await service.get_inflation_metrics()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
