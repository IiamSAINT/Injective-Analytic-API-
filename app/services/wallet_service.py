"""
Wallet Conversion Service - Address format conversion logic

Converts between EVM (0x...), Injective (inj1...), and any Cosmos Bech32
address format. All conversions are pure re-encoding of the same 20-byte
address — no network calls or private keys involved.
"""
import re
from typing import Optional, Tuple

import bech32


# ── Constants ────────────────────────────────────────────────────────────

INJECTIVE_PREFIX = "inj"
EVM_ADDRESS_REGEX = re.compile(r"^0x[0-9a-fA-F]{40}$")
BECH32_ADDRESS_REGEX = re.compile(r"^[a-z]+1[a-z0-9]{38,}$")


# ── Core conversion functions ────────────────────────────────────────────

def evm_to_injective(hex_address: str) -> str:
    """
    Convert an EVM hex address (0x...) to an Injective bech32 address (inj1...).
    """
    _validate_evm(hex_address)
    addr_bytes = bytes.fromhex(hex_address[2:])
    converted = bech32.bech32_encode(INJECTIVE_PREFIX, bech32.convertbits(addr_bytes, 8, 5))
    if converted is None:
        raise ValueError(f"Failed to bech32-encode address: {hex_address}")
    return converted


def injective_to_evm(inj_address: str) -> str:
    """
    Convert an Injective bech32 address (inj1...) to an EVM hex address (0x...).
    """
    addr_bytes = _decode_bech32(inj_address, expected_prefix=INJECTIVE_PREFIX)
    return "0x" + addr_bytes.hex()


def cosmos_to_injective(bech32_address: str) -> str:
    """
    Convert any Cosmos bech32 address (cosmos1..., osmo1..., terra1..., etc.)
    to the equivalent Injective address.
    """
    addr_bytes = _decode_bech32(bech32_address)
    converted = bech32.bech32_encode(INJECTIVE_PREFIX, bech32.convertbits(addr_bytes, 8, 5))
    if converted is None:
        raise ValueError(f"Failed to bech32-encode address: {bech32_address}")
    return converted


def injective_to_cosmos(inj_address: str, target_prefix: str) -> str:
    """
    Convert an Injective address to any other Cosmos chain prefix.
    """
    addr_bytes = _decode_bech32(inj_address, expected_prefix=INJECTIVE_PREFIX)
    converted = bech32.bech32_encode(target_prefix, bech32.convertbits(addr_bytes, 8, 5))
    if converted is None:
        raise ValueError(f"Failed to encode with prefix '{target_prefix}'")
    return converted


# ── Auto-detect & convert ────────────────────────────────────────────────

def detect_address_type(address: str) -> Tuple[str, Optional[str]]:
    """
    Detect whether an address is EVM hex or Cosmos bech32.

    Returns:
        (source_type, chain_prefix)
        - ("evm", None) for 0x addresses
        - ("injective", "inj") for inj1 addresses
        - ("cosmos", "<prefix>") for other bech32 addresses
    """
    if EVM_ADDRESS_REGEX.match(address):
        return ("evm", None)

    if BECH32_ADDRESS_REGEX.match(address):
        prefix = address.split("1", 1)[0]
        if prefix == INJECTIVE_PREFIX:
            return ("injective", INJECTIVE_PREFIX)
        return ("cosmos", prefix)

    raise ValueError(
        f"Unrecognised address format: '{address}'. "
        "Expected a 0x hex address or a bech32 address (e.g. inj1..., cosmos1..., osmo1...)."
    )


def convert_address(address: str) -> dict:
    """
    Auto-detect format and convert to both Injective and EVM representations.

    Returns a dict ready to be unpacked into WalletConversionResponse.
    """
    source_type, chain_prefix = detect_address_type(address)

    if source_type == "evm":
        inj_addr = evm_to_injective(address)
        evm_addr = address.lower()
    elif source_type == "injective":
        evm_addr = injective_to_evm(address)
        inj_addr = address
    else:  # cosmos
        inj_addr = cosmos_to_injective(address)
        evm_addr = injective_to_evm(inj_addr)

    return {
        "input_address": address,
        "injective_address": inj_addr,
        "evm_address": evm_addr,
        "source_type": source_type,
        "source_chain_prefix": chain_prefix,
    }


# ── Internal helpers ─────────────────────────────────────────────────────

def _validate_evm(address: str) -> None:
    """Validate an EVM hex address."""
    if not EVM_ADDRESS_REGEX.match(address):
        raise ValueError(
            f"Invalid EVM address: '{address}'. Must be 0x followed by 40 hex characters."
        )


def _decode_bech32(address: str, expected_prefix: Optional[str] = None) -> bytes:
    """
    Decode a bech32 address to raw 20-byte address bytes.
    Optionally validate the prefix.
    """
    decoded = bech32.bech32_decode(address)
    if decoded == (None, None) or decoded[1] is None:
        raise ValueError(f"Invalid bech32 address: '{address}'")

    prefix, data = decoded

    if expected_prefix and prefix != expected_prefix:
        raise ValueError(
            f"Expected prefix '{expected_prefix}', got '{prefix}' in address '{address}'"
        )

    addr_bytes_list = bech32.convertbits(data, 5, 8, False)
    if addr_bytes_list is None:
        raise ValueError(f"Failed to decode bech32 data for address: '{address}'")

    addr_bytes = bytes(addr_bytes_list)
    if len(addr_bytes) != 20:
        raise ValueError(
            f"Invalid address length: expected 20 bytes, got {len(addr_bytes)} for '{address}'"
        )

    return addr_bytes
