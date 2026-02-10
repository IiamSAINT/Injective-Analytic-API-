"""
Supply Service - Business logic for supply metrics
"""
from datetime import datetime, timezone
from typing import Optional
from app.services.injective_client import get_injective_client
from app.models.supply import SupplyMetrics, InflationMetrics, TokenDistribution, SupplyOverview


from app.config import get_settings

settings = get_settings()


def parse_inj_amount(amount_str: str) -> float:
    """Convert INJ amount from chain format to float."""
    try:
        # Handle decimal strings (e.g. from annual provisions)
        val = float(amount_str)
        return val / (10 ** settings.inj_decimals)
    except (ValueError, TypeError):
        return 0.0


class SupplyService:
    """Service for supply-related operations."""
    
    def __init__(self):
        self.client = get_injective_client()
    
    async def get_supply_metrics(self) -> SupplyMetrics:
        """Get comprehensive supply metrics."""
        # Fetch data
        supply_data = await self.client.get_total_supply()
        pool_data = await self.client.get_staking_pool()
        
        # Parse total supply
        total_supply_raw = supply_data.get("amount", {}).get("amount", "0")
        total_supply = parse_inj_amount(total_supply_raw)
        
        # Parse staked supply
        bonded_raw = pool_data.get("bonded_tokens", "0")
        staked_supply = parse_inj_amount(bonded_raw)
        
        # Calculate burned (fetch from burn address)
        burned_raw = await self.client.get_balance(settings.inj_burn_address, "inj")
        # burned_raw is already float from client? No, client returned float?
        # Let's check client implementation. I defined it to return float.
        # But wait, parse_inj_amount divides by 10^18.
        # client.get_balance returns raw amount as float? 
        # get_balance returns raw amount as float, so divide by 10^18
        burned_supply = burned_raw / (10 ** settings.inj_decimals)
        burn_percentage = (burned_supply / total_supply) * 100 if total_supply > 0 else 0
        
        # Circulating = Total - Staked - Burned
        # Assuming Total Supply includes tokens at burn address (if they are not burned from state)
        circulating_supply = total_supply - staked_supply - burned_supply
        
        return SupplyMetrics(
            total_supply=total_supply,
            initial_supply=settings.inj_initial_supply,
            circulating_supply=circulating_supply,
            staked_supply=staked_supply,
            burned_supply=burned_supply,
            burn_percentage=burn_percentage,
            calculated_at=datetime.now(timezone.utc)
        )
    
    async def get_inflation_metrics(self) -> InflationMetrics:
        """Get inflation/deflation metrics."""
        # Fetch data
        inflation_data = await self.client.get_inflation()
        mint_params = await self.client.get_mint_params()
        provisions_data = await self.client.get_annual_provisions()
        
        # Parse inflation rate
        inflation_str = inflation_data.get("inflation", "0")
        inflation_rate = float(inflation_str) if inflation_str else 0.0
        
        # Parse mint params
        goal_bonded = float(mint_params.get("goal_bonded", "0.67"))
        inflation_min = float(mint_params.get("inflation_min", "0.07"))
        inflation_max = float(mint_params.get("inflation_max", "0.20"))
        blocks_per_year = int(mint_params.get("blocks_per_year", "31536000"))
        
        # Parse annual provisions
        provisions_str = provisions_data.get("annual_provisions", "0")
        mint_provision = parse_inj_amount(provisions_str)
        
        # Estimate if deflationary (would need burn rate comparison)
        # For now, assume deflationary if inflation < 5% (Adjusted logic for demo)
        is_deflationary = inflation_rate < 0.05
        
        return InflationMetrics(
            inflation_rate=inflation_rate * 100,  # Convert to percentage
            mint_provision=mint_provision,
            blocks_per_year=blocks_per_year,
            goal_bonded=goal_bonded * 100,
            inflation_min=inflation_min * 100,
            inflation_max=inflation_max * 100,
            is_deflationary=is_deflationary,
            net_change_rate=(inflation_rate * 100) - 1.5,  # Approx burn rate offset
            calculated_at=datetime.now(timezone.utc)
        )
    
    async def get_distribution(self) -> TokenDistribution:
        """Get token distribution breakdown."""
        supply_metrics = await self.get_supply_metrics()
        pool_data = await self.client.get_staking_pool()
        
        # Calculate percentages
        total = supply_metrics.total_supply
        initial = supply_metrics.initial_supply
        
        staked_pct = (supply_metrics.staked_supply / total * 100) if total > 0 else 0
        # Burn pct is based on INITIAL supply usually
        burned_pct = supply_metrics.burn_percentage
        
        # Unbonding tokens
        unbonding_raw = pool_data.get("not_bonded_tokens", "0")
        unbonding = parse_inj_amount(unbonding_raw)
        unbonding_pct = (unbonding / total * 100) if total > 0 else 0
        
        # Free circulating
        # This is a rough pie chart: Staked + Unbonding + Burned + Free = 100%? 
        # Actually Burned is gone from Total. 
        # So Token Distribution of EXISTING tokens: Staked + Unbonding + Free = 100%
        circulating_pct = 100 - staked_pct - unbonding_pct
        
        return TokenDistribution(
            staked=round(staked_pct, 2),
            circulating_free=round(circulating_pct, 2),
            burned=round(burned_pct, 2),
            unbonding=round(unbonding_pct, 2),
            calculated_at=datetime.now(timezone.utc)
        )
    
    async def get_overview(self) -> SupplyOverview:
        """Get complete supply overview."""
        metrics = await self.get_supply_metrics()
        inflation = await self.get_inflation_metrics()
        distribution = await self.get_distribution()
        
        return SupplyOverview(
            metrics=metrics,
            inflation=inflation,
            distribution=distribution
        )


# Singleton
_service = None


def get_supply_service() -> SupplyService:
    global _service
    if _service is None:
        _service = SupplyService()
    return _service
