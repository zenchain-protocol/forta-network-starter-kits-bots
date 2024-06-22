import asyncio
import pytest
from datetime import datetime
from forta_bot_sdk import (
    FindingSeverity,
)

import agent
from evmdasm import EvmBytecode
from web3_mock import (
    BENIGN_CONTRACT,
    CONTRACT_NO_ADDRESS,
    CONTRACT_WITH_ADDRESS,
    EOA_ADDRESS,
    MALICIOUS_TOKEN_CONTRACT,
    MALICIOUS_TOKEN_CONTRACT_DEPLOYER,
    MALICIOUS_TOKEN_CONTRACT_DEPLOYER_NONCE,
    SHORT_CONTRACT,
    Web3Mock,
)
from unittest.mock import patch

w3 = Web3Mock()
pytest_plugins = ("pytest_asyncio",)

# Mock secrets data
SECRETS_JSON = {
    "apiKeys": {
        "ETHERSCAN_TOKEN": "your-etherscan-api-key",
        "POLYGONSCAN_TOKEN": "your-polygonscan-api-key",
        "BSCSCAN_TOKEN": "your-bscscan-api-key",
        "ARBISCAN_TOKEN": "your-arbiscan-api-key",
        "OPTIMISTICSCAN_TOKEN": "your-optimisticscan-api-key",
        "FTMSCAN_TOKEN": "your-ftmscan-api-key",
        "SNOWTRACE_TOKEN": "your-snowtrace-api-key",
        "BLOCKSCOUT_TOKEN": "your-blockscout-api-key",
        "ZETTABLOCK": "your-zettablock-api-key",
    }
}

# Fixture to mock get_secrets function globally for all tests
@pytest.fixture(autouse=True)
def mock_get_secrets():
    with patch("agent.get_secrets", return_value=SECRETS_JSON):
        yield

# Fixture to patch calculate_alert_rate with a random value
@pytest.fixture
def mock_calculate_alert_rate():
    with patch("findings.calculate_alert_rate", return_value=random.uniform(0.1, 1.0)):
        yield

class TestMaliciousSmartContractML:
    @pytest.mark.asyncio
    async def test_is_contract_eoa(self):
        assert not await agent.is_contract(
            w3, EOA_ADDRESS
        ), "EOA shouldn't be identified as a contract"

    @pytest.mark.asyncio
    async def test_is_contract_contract(self):
        assert await agent.is_contract(
            w3, CONTRACT_NO_ADDRESS
        ), "Contract should be identified as a contract"

    @pytest.mark.asyncio
    async def test_opcode_addresses_eoa(self):
        # EOAs don't have bytecode or opcodes
        bytecode = await w3.eth.get_code(EOA_ADDRESS)
        opcodes = EvmBytecode(bytecode.hex()).disassemble()
        _, addresses = await agent.get_features(w3, opcodes, EOA_ADDRESS)
        assert len(addresses) == 0, "should be empty"

    @pytest.mark.asyncio
    async def test_opcode_addresses_no_addr(self):
        bytecode = await w3.eth.get_code(CONTRACT_NO_ADDRESS)
        opcodes = EvmBytecode(bytecode.hex()).disassemble()
        _, addresses = await agent.get_features(w3, opcodes, EOA_ADDRESS)
        assert len(addresses) == 0, "should be empty"

    @pytest.mark.asyncio
    async def test_opcode_addresses_with_addr(self):
        bytecode = await w3.eth.get_code(CONTRACT_WITH_ADDRESS)
        opcodes = EvmBytecode(bytecode.hex()).disassemble()
        _, addresses = await agent.get_features(w3, opcodes, EOA_ADDRESS)

        assert len(addresses) == 1, "should not be empty"

    @pytest.mark.asyncio
    async def test_storage_addresses_with_addr(self):
        addresses = await agent.get_storage_addresses(w3, CONTRACT_WITH_ADDRESS)
        assert len(addresses) == 1, "should not be empty"

    @pytest.mark.asyncio
    async def test_storage_addresses_on_eoa(self):
        addresses = await agent.get_storage_addresses(w3, EOA_ADDRESS)
        assert len(addresses) == 0, "should be empty; EOA has no storage"

    def test_calc_contract_address(self):
        contract_address = agent.calc_contract_address(w3, EOA_ADDRESS, 9)
        assert (
            contract_address == "0x728ad672409DA288cA5B9AA85D1A55b803bA97D7"
        ), "should be the same contract address"

    @pytest.mark.asyncio
    async def test_get_features(self):
        bytecode = await w3.eth.get_code(MALICIOUS_TOKEN_CONTRACT)
        opcodes = EvmBytecode(bytecode.hex()).disassemble()
        features, _ = await agent.get_features(w3, opcodes, EOA_ADDRESS)
        assert len(features) == 24312, "incorrect features length obtained"

    @pytest.mark.asyncio
    async def test_finding_MALICIOUS_TOKEN_CONTRACT_creation(self):
        await agent.initialize()
        code = await w3.eth.get_code(MALICIOUS_TOKEN_CONTRACT)
        findings = await agent.detect_malicious_token_contract(
            w3, MALICIOUS_TOKEN_CONTRACT_DEPLOYER, MALICIOUS_TOKEN_CONTRACT, code
        )
        assert len(findings) == 1, "this should have triggered a finding"
        finding = next(
            (x for x in findings if x.alert_id == "SUSPICIOUS-TOKEN-CONTRACT-CREATION"),
            None,
        )
        assert finding.severity == FindingSeverity.High

    @pytest.mark.asyncio
    async def test_detect_malicious_token_contract_benign(self):
        await agent.initialize()
        bytecode = await w3.eth.get_code(BENIGN_CONTRACT)
        findings = await agent.detect_malicious_token_contract(
            w3, EOA_ADDRESS, BENIGN_CONTRACT, bytecode
        )
        assert len(findings) == 1
        finding = findings[0]
        assert finding.alert_id == "SAFE-TOKEN-CONTRACT-CREATION"

    @pytest.mark.asyncio
    async def test_detect_malicious_token_contract_short(self):
        await agent.initialize()
        bytecode = await w3.eth.get_code(SHORT_CONTRACT)
        findings = await agent.detect_malicious_token_contract(
            w3, EOA_ADDRESS, SHORT_CONTRACT, bytecode
        )
        assert len(findings) == 0, "this should not have triggered a finding"
