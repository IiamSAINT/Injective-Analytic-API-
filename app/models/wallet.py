"""
Pydantic models for wallet address conversion
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class WalletConversionResponse(BaseModel):
    """Result of a single address conversion."""
    input_address: str = Field(..., description="The original input address")
    injective_address: str = Field(..., description="Injective bech32 address (inj1...)")
    evm_address: str = Field(..., description="EVM hex address (0x...)")
    source_type: str = Field(..., description="Detected source: 'evm', 'injective', or 'cosmos'")
    source_chain_prefix: Optional[str] = Field(
        None, description="Bech32 prefix of source address if Cosmos-based (e.g. cosmos, osmo, terra)"
    )


class BatchConversionRequest(BaseModel):
    """Request body for batch conversion."""
    addresses: List[str] = Field(
        ..., min_length=1, max_length=50,
        description="List of addresses to convert (max 50)"
    )


class BatchConversionResponse(BaseModel):
    """Result of a batch address conversion."""
    conversions: List[WalletConversionResponse]
    total: int = Field(..., description="Number of addresses converted")
    errors: List[dict] = Field(
        default_factory=list,
        description="Addresses that failed conversion with error messages"
    )
