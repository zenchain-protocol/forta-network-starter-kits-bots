import time
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

from forta_bot_sdk import (
    FindingSeverity,
    FindingType,
    TransactionEvent,
    EntityType,
)
import asyncio
import agent
from web3_mock import CONTRACT_NO_ADDRESS, CONTRACT_WITH_ADDRESS, EOA_ADDRESS, Web3Mock
from constants import CHAIN_ID
from blockexplorer_mock import BlockExplorerMock

w3 = Web3Mock()
blockexplorer = BlockExplorerMock(1)

@pytest.fixture(autouse=True)
@patch("agent.get_secrets", return_value=blockexplorer.SECRETS_JSON)
@patch("agent.BlockExplorer", return_value=blockexplorer)
def setup(mock_get_secrets, mock_block_explorer):
    asyncio.run(agent.initialize())


class TestUnverifiedContractAgent:

    def test_get_opcode_addresses_eoa(self):
        addresses = agent.get_opcode_addresses(w3, EOA_ADDRESS)
        assert len(addresses) == 0, "should be empty"

    def test_get_opcode_addresses_no_addr(self):
        addresses = agent.get_opcode_addresses(w3, CONTRACT_NO_ADDRESS)
        assert len(addresses) == 0, "should not be empty"

    def test_get_opcode_addresses_with_addr(self):
        addresses = agent.get_opcode_addresses(w3, CONTRACT_WITH_ADDRESS)
        assert len(addresses) == 1, "should not be empty"

    def test_storage_addresses_with_addr(self):
        addresses = agent.get_opcode_addresses(w3, CONTRACT_WITH_ADDRESS)
        assert len(addresses) == 1, "should not be empty"

    def test_storage_addresses_on_eoa(self):
        addresses = agent.get_opcode_addresses(w3, EOA_ADDRESS)
        assert len(addresses) == 0, "should be empty; EOA has no storage"

    def test_calc_contract_address(self):
        contract_address = agent.calc_contract_address(w3, EOA_ADDRESS, 9)
        assert (
            contract_address == "0x728ad672409DA288cA5B9AA85D1A55b803bA97D7"
        ), "should be the same contract address"

    @patch("src.findings.calculate_alert_rate", return_value=1.0)
    def test_detect_unverified_contract_with_unverified_contract_no_trace(self, mocker):
        tx_event = TransactionEvent(
            {
                "transaction": {
                    "hash": "0",
                    "from": EOA_ADDRESS,
                    "nonce": 9,
                },
                "block": {
                    "number": 0,
                    "timestamp": datetime.now().timestamp(),
                },
                "receipt": {"logs": []},
                "chain_id": CHAIN_ID,
            }
        )
        agent.cache_contract_creation(w3, tx_event)
        time.sleep(2)
        agent.detect_unverified_contract_creation(
            w3, blockexplorer, wait_time=0, infinite=False
        )
        assert len(agent.FINDINGS_CACHE) == 1, "should have 1 finding"
        assert "anomaly_score" in agent.FINDINGS_CACHE[0].metadata
        assert (
            float(agent.FINDINGS_CACHE[0].metadata["anomaly_score"]) > 0
        ), "anomaly score should be greater than 0"
        assert (
            agent.FINDINGS_CACHE[0].labels[0].entity.lower() == EOA_ADDRESS.lower()
        ), "should have EOA address as label"
        assert (
            agent.FINDINGS_CACHE[0].labels[0].entity_type == EntityType.Address
        ), "should have label_type address"
        assert (
            agent.FINDINGS_CACHE[0].labels[0].label == "attacker"
        ), "should have attacker as label"
        assert (
            agent.FINDINGS_CACHE[0].labels[0].confidence == 0.3
        ), "should have 0.3 as label confidence"
        assert (
            agent.FINDINGS_CACHE[0].labels[1].entity
            == "0x728ad672409DA288cA5B9AA85D1A55b803bA97D7"
        ), "should have contract address as label"
        assert (
            agent.FINDINGS_CACHE[0].labels[1].label == "attacker_contract"
        ), "should have attacker as label"
        assert (
            agent.FINDINGS_CACHE[0].labels[1].confidence == 0.3
        ), "should have 0.3 as label confidence"
        assert (
            agent.FINDINGS_CACHE[0].labels[1].entity_type == EntityType.Address
        ), "should have label_type address"

    def test_detect_unverified_contract_with_unverified_contract_trace(self):
        tx_event = TransactionEvent(
            {
                "transaction": {
                    "hash": "0",
                    "from": EOA_ADDRESS,
                    "to": "0x0000000000000000000000000000000000000000",
                    "nonce": 9,
                },
                "block": {
                    "number": 0,
                    "timestamp": datetime.now().timestamp(),
                },
                "traces": [
                    {
                        "type": "create",
                        "action": {
                            "from": EOA_ADDRESS,
                            "value": 1,
                        },
                    }
                ],
                "receipt": {"logs": []},
            }
        )

        agent.cache_contract_creation(w3, tx_event)
        time.sleep(2)
        agent.detect_unverified_contract_creation(
            w3, blockexplorer, wait_time=0, infinite=False
        )
        assert len(agent.FINDINGS_CACHE) == 1, "should have 1 finding"
        finding = next(
            (
                x
                for x in agent.FINDINGS_CACHE
                if x.alert_id == "UNVERIFIED-CODE-CONTRACT-CREATION"
            ),
            None,
        )
        assert finding.severity == FindingSeverity.Medium
        assert finding.type == FindingType.Suspicious
        assert (
            finding.description.lower()
            == f"{EOA_ADDRESS} created contract 0x728ad672409DA288cA5B9AA85D1A55b803bA97D7".lower()
        )
        assert len(finding.metadata) > 0

    def test_detect_unverified_contract_with_verified_contract(self):
        tx_event = TransactionEvent(
            {
                "transaction": {
                    "hash": "0",
                    "from": EOA_ADDRESS,
                    "nonce": 10,  # verified contract
                },
                "block": {
                    "number": 0,
                    "timestamp": datetime.now().timestamp(),
                },
                "traces": [
                    {
                        "type": "create",
                        "action": {
                            "from": EOA_ADDRESS,
                            "value": 1,
                        },
                    }
                ],
                "receipt": {"logs": []},
            }
        )

        agent.cache_contract_creation(w3, tx_event)
        time.sleep(2)
        agent.detect_unverified_contract_creation(
            w3, blockexplorer, wait_time=0, infinite=False
        )

        assert len(agent.FINDINGS_CACHE) == 0, "should have 0 finding"

    def test_detect_unverified_contract_call_only(self):
        tx_event = TransactionEvent(
            {
                "transaction": {
                    "hash": "0",
                    "from": EOA_ADDRESS,
                    "nonce": 7,
                    "to": "0x0000000000000000000000000000000000000000",
                },
                "block": {
                    "number": 0,
                    "timestamp": datetime.now().timestamp(),
                },
                "traces": [
                    {
                        "type": "call",
                        "action": {
                            "from": EOA_ADDRESS,
                            "to": "0x728ad672409DA288cA5B9AA85D1A55b803bA97D7",  # unverified contract
                            "value": 1,
                        },
                    }
                ],
                "receipt": {"logs": []},
            }
        )

        agent.cache_contract_creation(w3, tx_event)
        time.sleep(2)
        agent.detect_unverified_contract_creation(
            w3, blockexplorer, wait_time=0, infinite=False
        )
        assert len(agent.FINDINGS_CACHE) == 0, "should have 0 finding"