"""
Pydantic models for supply data
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SupplyMetrics(BaseModel):
    """Token supply metrics."""
    total_supply: float = Field(..., description="Current total supply")
    initial_supply: float = Field(100_000_000, description="Initial supply at launch")
    circulating_supply: float = Field(..., description="Circulating supply")
    staked_supply: float = Field(..., description="Supply locked in staking")
    burned_supply: float = Field(..., description="Total supply burned")
    burn_percentage: float = Field(..., description="% of initial supply burned")
    calculated_at: datetime = Field(default_factory=lambda: datetime.now())


class InflationMetrics(BaseModel):
    """Inflation/deflation metrics."""
    inflation_rate: float = Field(..., description="Current annual inflation rate")
    mint_provision: float = Field(..., description="Annual mint provision")
    blocks_per_year: int = Field(..., description="Estimated blocks per year")
    goal_bonded: float = Field(..., description="Target bonding ratio")
    inflation_min: float = Field(..., description="Minimum inflation rate")
    inflation_max: float = Field(..., description="Maximum inflation rate")
    is_deflationary: bool = Field(..., description="Whether net supply is decreasing")
    net_change_rate: float = Field(..., description="Net supply change rate (inflation - burns)")
    calculated_at: datetime = Field(default_factory=lambda: datetime.now())


class TokenDistribution(BaseModel):
    """Token distribution breakdown."""
    staked: float = Field(..., description="% staked")
    circulating_free: float = Field(..., description="% freely circulating")
    burned: float = Field(..., description="% burned from initial supply")
    unbonding: float = Field(..., description="% in unbonding period")
    calculated_at: datetime = Field(default_factory=lambda: datetime.now())


class SupplyOverview(BaseModel):
    """Complete supply overview."""
    metrics: SupplyMetrics
    inflation: InflationMetrics
    distribution: TokenDistribution
