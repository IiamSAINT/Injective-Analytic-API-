"""
Wallet Router - Address conversion endpoints
"""
from fastapi import APIRouter, HTTPException

from app.services.wallet_service import (
    convert_address,
    evm_to_injective,
    injective_to_evm,
)
from app.models.wallet import (
    WalletConversionResponse,
    BatchConversionRequest,
    BatchConversionResponse,
)

router = APIRouter()


@router.get("/wallet/convert/{address}", response_model=WalletConversionResponse)
async def auto_convert_address(address: str):
    """
    Auto-detect and convert any wallet address to Injective format.

    Accepts:
    - **EVM hex** addresses (`0x...`)
    - **Injective** addresses (`inj1...`)
    - **Any Cosmos** bech32 address (`cosmos1...`, `osmo1...`, `terra1...`, etc.)

    Returns the equivalent Injective (`inj1...`) and EVM (`0x...`) addresses.
    """
    try:
        result = convert_address(address)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


@router.post("/wallet/convert/batch", response_model=BatchConversionResponse)
async def batch_convert_addresses(body: BatchConversionRequest):
    """
    Convert up to 50 addresses in a single request.

    Each address is auto-detected and converted independently.
    Successfully converted addresses appear in `conversions`;
    failures appear in `errors` with their error messages.
    """
    conversions = []
    errors = []

    for addr in body.addresses:
        try:
            result = convert_address(addr)
            conversions.append(result)
        except ValueError as e:
            errors.append({"address": addr, "error": str(e)})

    return BatchConversionResponse(
        conversions=conversions,
        total=len(conversions),
        errors=errors,
    )


@router.get("/wallet/convert/evm-to-inj/{address}", response_model=WalletConversionResponse)
async def convert_evm_to_inj(address: str):
    """
    Explicitly convert an EVM hex address (`0x...`) to Injective format.
    """
    try:
        inj_addr = evm_to_injective(address)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return WalletConversionResponse(
        input_address=address,
        injective_address=inj_addr,
        evm_address=address.lower(),
        source_type="evm",
        source_chain_prefix=None,
    )


@router.get("/wallet/convert/inj-to-evm/{address}", response_model=WalletConversionResponse)
async def convert_inj_to_evm(address: str):
    """
    Explicitly convert an Injective address (`inj1...`) to EVM hex format.
    """
    try:
        evm_addr = injective_to_evm(address)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return WalletConversionResponse(
        input_address=address,
        injective_address=address,
        evm_address=evm_addr,
        source_type="injective",
        source_chain_prefix="inj",
    )
