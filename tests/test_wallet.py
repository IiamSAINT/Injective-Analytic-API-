"""
Tests for Wallet Address Conversion Feature
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.wallet_service import (
    evm_to_injective,
    injective_to_evm,
    cosmos_to_injective,
    convert_address,
    detect_address_type,
)

client = TestClient(app)

# ── Known address pairs (same 20-byte key) ──────────────────────────────
# These are real-format addresses sharing the same underlying bytes.
EVM_ADDR = "0xAF79152AC5dF276D9A8e1E2E22822f9713474902"
# Pre-compute the expected INJ address for this EVM address
EXPECTED_INJ = evm_to_injective(EVM_ADDR)


# ── Unit tests: service layer ────────────────────────────────────────────

class TestEvmToInjective:
    def test_valid_conversion(self):
        result = evm_to_injective(EVM_ADDR)
        assert result.startswith("inj1")
        assert len(result) > 10

    def test_lowercase_input(self):
        result = evm_to_injective(EVM_ADDR.lower())
        assert result == EXPECTED_INJ

    def test_invalid_hex(self):
        with pytest.raises(ValueError, match="Invalid EVM address"):
            evm_to_injective("0xINVALID")

    def test_too_short(self):
        with pytest.raises(ValueError, match="Invalid EVM address"):
            evm_to_injective("0x1234")

    def test_missing_prefix(self):
        with pytest.raises(ValueError, match="Invalid EVM address"):
            evm_to_injective("AF79152AC5dF276D9A8e1E2E22822f9713474902")


class TestInjectiveToEvm:
    def test_roundtrip(self):
        """EVM → INJ → EVM should return the same address."""
        inj = evm_to_injective(EVM_ADDR)
        evm_back = injective_to_evm(inj)
        assert evm_back == EVM_ADDR.lower()

    def test_invalid_bech32(self):
        with pytest.raises(ValueError):
            injective_to_evm("inj1invalid")

    def test_wrong_prefix(self):
        """Should reject non-inj bech32 addresses."""
        cosmos_addr = cosmos_to_injective(EXPECTED_INJ)  # this is inj->inj, still valid
        # Create a cosmos address from the same bytes to test prefix check
        from app.services.wallet_service import injective_to_cosmos
        cosmos = injective_to_cosmos(EXPECTED_INJ, "cosmos")
        with pytest.raises(ValueError, match="Expected prefix 'inj'"):
            injective_to_evm(cosmos)


class TestCosmosToInjective:
    def test_cosmos_prefix(self):
        from app.services.wallet_service import injective_to_cosmos
        cosmos = injective_to_cosmos(EXPECTED_INJ, "cosmos")
        result = cosmos_to_injective(cosmos)
        assert result == EXPECTED_INJ

    def test_osmo_prefix(self):
        from app.services.wallet_service import injective_to_cosmos
        osmo = injective_to_cosmos(EXPECTED_INJ, "osmo")
        result = cosmos_to_injective(osmo)
        assert result == EXPECTED_INJ

    def test_terra_prefix(self):
        from app.services.wallet_service import injective_to_cosmos
        terra = injective_to_cosmos(EXPECTED_INJ, "terra")
        result = cosmos_to_injective(terra)
        assert result == EXPECTED_INJ


class TestDetectAddressType:
    def test_evm(self):
        stype, prefix = detect_address_type(EVM_ADDR)
        assert stype == "evm"
        assert prefix is None

    def test_injective(self):
        stype, prefix = detect_address_type(EXPECTED_INJ)
        assert stype == "injective"
        assert prefix == "inj"

    def test_cosmos(self):
        from app.services.wallet_service import injective_to_cosmos
        cosmos = injective_to_cosmos(EXPECTED_INJ, "cosmos")
        stype, prefix = detect_address_type(cosmos)
        assert stype == "cosmos"
        assert prefix == "cosmos"

    def test_invalid(self):
        with pytest.raises(ValueError, match="Unrecognised"):
            detect_address_type("not_an_address")


class TestConvertAddress:
    def test_from_evm(self):
        result = convert_address(EVM_ADDR)
        assert result["injective_address"] == EXPECTED_INJ
        assert result["evm_address"] == EVM_ADDR.lower()
        assert result["source_type"] == "evm"

    def test_from_injective(self):
        result = convert_address(EXPECTED_INJ)
        assert result["evm_address"] == EVM_ADDR.lower()
        assert result["source_type"] == "injective"

    def test_from_cosmos(self):
        from app.services.wallet_service import injective_to_cosmos
        cosmos = injective_to_cosmos(EXPECTED_INJ, "osmo")
        result = convert_address(cosmos)
        assert result["injective_address"] == EXPECTED_INJ
        assert result["source_type"] == "cosmos"
        assert result["source_chain_prefix"] == "osmo"


# ── Integration tests: API endpoints ────────────────────────────────────

class TestAutoConvertEndpoint:
    def test_evm_address(self):
        response = client.get(f"/api/v1/wallet/convert/{EVM_ADDR}")
        assert response.status_code == 200
        data = response.json()
        assert data["injective_address"].startswith("inj1")
        assert data["source_type"] == "evm"

    def test_inj_address(self):
        response = client.get(f"/api/v1/wallet/convert/{EXPECTED_INJ}")
        assert response.status_code == 200
        data = response.json()
        assert data["evm_address"].startswith("0x")
        assert data["source_type"] == "injective"

    def test_invalid_address(self):
        response = client.get("/api/v1/wallet/convert/garbage123")
        assert response.status_code == 400


class TestExplicitEndpoints:
    def test_evm_to_inj(self):
        response = client.get(f"/api/v1/wallet/convert/evm-to-inj/{EVM_ADDR}")
        assert response.status_code == 200
        data = response.json()
        assert data["injective_address"].startswith("inj1")

    def test_inj_to_evm(self):
        response = client.get(f"/api/v1/wallet/convert/inj-to-evm/{EXPECTED_INJ}")
        assert response.status_code == 200
        data = response.json()
        assert data["evm_address"].startswith("0x")


class TestBatchEndpoint:
    def test_batch_conversion(self):
        response = client.post(
            "/api/v1/wallet/convert/batch",
            json={"addresses": [EVM_ADDR, EXPECTED_INJ]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["conversions"]) == 2

    def test_batch_with_errors(self):
        response = client.post(
            "/api/v1/wallet/convert/batch",
            json={"addresses": [EVM_ADDR, "invalid_addr"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["errors"]) == 1

    def test_batch_empty(self):
        response = client.post(
            "/api/v1/wallet/convert/batch",
            json={"addresses": []},
        )
        assert response.status_code == 422  # validation error: min_length=1
