import logging
import sys
import threading
from datetime import datetime, timedelta
from os import environ
import concurrent.futures
from functools import lru_cache

import forta_bot_sdk
import rlp
from forta_bot_sdk import scan_ethereum, scan_alerts, run_health_check, fetch_jwt, decode_jwt
from hexbytes import HexBytes
from pyevmasm import disassemble_hex
from web3 import Web3, AsyncWeb3
import time
import asyncio
import traceback

from blockexplorer import BlockExplorer
from constants import CONTRACT_SLOT_ANALYSIS_DEPTH, WAIT_TIME, CONCURRENT_SIZE
from findings import UnverifiedCodeContractFindings
from storage import get_secrets
from constants import CHAIN_ID, EVM_RPC

FINDINGS_CACHE = []
THREAD_STARTED = False
CREATED_CONTRACTS = {}  # contract and creation timestamp
LOCK = threading.Lock()

root = logging.getLogger()
root.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
root.addHandler(handler)

async def initialize():
    """
    this function initializes the state variables that are tracked across tx and blocks
    it is called from test to reset state between tests
    """
    global FINDINGS_CACHE
    FINDINGS_CACHE = []

    global THREAD_STARTED
    THREAD_STARTED = False

    global CREATED_CONTRACTS
    CREATED_CONTRACTS = {}

    global BOT_ID
    jwt = await fetch_jwt({})
    decoded_token_data = decode_jwt(jwt)
    BOT_ID = decoded_token_data["payload"]["bot-id"]
    environ['FORTA_BOT_ID'] = environ.get('FORTA_BOT_ID', BOT_ID)

    global SECRETS_JSON 
    SECRETS_JSON = await get_secrets()

    global BLOCK_EXPLORER
    BLOCK_EXPLORER = BlockExplorer(CHAIN_ID, SECRETS_JSON)

    environ["ZETTABLOCK_API_KEY"] = SECRETS_JSON["apiKeys"]["ZETTABLOCK"]


def calc_contract_address(w3, address, nonce) -> str:
    """
    this function calculates the contract address from sender/nonce
    :return: contract address: str
    """

    address_bytes = bytes.fromhex(address[2:].lower())
    return Web3.to_checksum_address(Web3.keccak(rlp.encode([address_bytes, nonce]))[-20:])


@lru_cache(maxsize=12800)
def is_contract(w3, address) -> bool:
    """
    this function determines whether address is a contract
    :return: is_contract: bool
    """
    if address is None:
        return True
    try:
        code = w3.eth.get_code(Web3.to_checksum_address(address))
        return code != HexBytes("0x")
    except Exception as e:
        logging.warn(f"Web3 error for is_contract method", {address: address, e: e})
        return False

@lru_cache(maxsize=12800)
def get_storage_addresses(w3, address) -> set:
    """
    this function returns the addresses that are references in the storage of a contract (first CONTRACT_SLOT_ANALYSIS_DEPTH slots)
    :return: address_list: list (only returning contract addresses)
    """
    start_time = time.time()

    if address is None:
        return set()

    address_set = set()

    def get_storage_at_slot(size):
        for i in size:
            try:
                mem = w3.eth.get_storage_at(Web3.to_checksum_address(address), i)
                if mem != HexBytes(
                    "0x0000000000000000000000000000000000000000000000000000000000000000"
                ):
                    # looking at both areas of the storage slot as - depending on packing - the address could be at the beginning or the end.
                    if is_contract(w3, mem[0:20]):
                        address_set.add(Web3.to_checksum_address(mem[0:20].hex()))
                    if is_contract(w3, mem[12:]):
                        address_set.add(Web3.to_checksum_address(mem[12:].hex()))
            except Exception as e:
                logging.warning(
                    f"Web3 Error at get_storage_at method", {address: address, e: e}
                )

    concurrent_sizes = [
        range(i, min(i + CONCURRENT_SIZE, CONTRACT_SLOT_ANALYSIS_DEPTH))
        for i in range(0, CONTRACT_SLOT_ANALYSIS_DEPTH, CONCURRENT_SIZE)
    ]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(get_storage_at_slot, concurrent_sizes)

    end_time = time.time()

    logging.info(f"get_storage_addresses took {end_time - start_time} seconds")

    return address_set


@lru_cache(maxsize=12800)
def get_opcode_addresses(w3, address) -> set:
    """
    this function returns the addresses that are references in the opcodes of a contract
    :return: address_list: list (only returning contract addresses)
    """
    start_time = time.time()

    if address is None:
        return set()

    code = w3.eth.get_code(Web3.to_checksum_address(address))
    opcode = disassemble_hex(code.hex())

    address_set = set()
    for op in opcode.splitlines():
        for param in op.split(" "):
            if param.startswith("0x") and len(param) == 42:
                if is_contract(w3, param):
                    address_set.add(Web3.to_checksum_address(param))

    end_time = time.time()

    logging.info(f"get_opcode_addresses took {end_time - start_time} seconds")

    return address_set


def cache_contract_creation(
    w3, transaction_event: forta_bot_sdk.TransactionEvent
):
    global CREATED_CONTRACTS

    logging.info(
        f"Scanning transaction {transaction_event.transaction.hash} on chain {CHAIN_ID}"
    )

    with LOCK:
        created_contract_addresses = []
        if transaction_event.to is None:
            nonce = transaction_event.transaction.nonce
            created_contract_address = calc_contract_address(
                w3, transaction_event.from_, nonce
            )

            logging.info(
                f"Added contract {created_contract_address} to cache. Timestamp: {transaction_event.timestamp}"
            )
            CREATED_CONTRACTS[created_contract_address] = transaction_event

        for trace in transaction_event.traces:
            if trace.type == "create":
                if (
                    transaction_event.from_ == trace.action.from_
                    or trace.action.from_ in created_contract_addresses
                ):
                    if transaction_event.from_ == trace.action.from_:
                        nonce = transaction_event.transaction.nonce
                        created_contract_address = calc_contract_address(w3, trace.action.from_, nonce)
                    else:
                        # For contracts creating other contracts, get the nonce using Web3
                        nonce = w3.eth.getTransactionCount(Web3.to_checksum_address(trace.action.from_), transaction_event.block_number)
                        created_contract_address = calc_contract_address(w3, trace.action.from_, nonce - 1)

                    if created_contract_address not in CREATED_CONTRACTS:
                        logging.info(
                            f"Added contract {created_contract_address} to cache. Timestamp: {transaction_event.timestamp}"
                        )

                        CREATED_CONTRACTS[created_contract_address] = transaction_event

    contracts_count = len(CREATED_CONTRACTS.items())
    logging.info(f"Created Contracts Count = {contracts_count}")


def detect_unverified_contract_creation(
    w3, blockexplorer, wait_time=WAIT_TIME, infinite=True
):
    global CREATED_CONTRACTS
    global FINDINGS_CACHE

    try:
        while True:
            with LOCK:
                for (
                    created_contract_address,
                    transaction_event,
                ) in CREATED_CONTRACTS.copy().items():
                    logging.info(
                        f"Evaluating contract {created_contract_address} from cache."
                    )
                    created_contract_addresses = []
                    if transaction_event.to is None:
                        logging.info(
                            f"Contract {created_contract_address} created by EOA."
                        )
                        nonce = transaction_event.transaction.nonce
                        created_contract_address = calc_contract_address(
                            w3, transaction_event.from_, nonce
                        )
                        if (
                            datetime.now()
                            - datetime.fromtimestamp(transaction_event.timestamp)
                        ) > timedelta(minutes=wait_time):
                            logging.info(
                                f"Evaluating contract {created_contract_address} from cache. Is old enough."
                            )
                            if not BLOCK_EXPLORER.is_verified(created_contract_address):
                                logging.info(
                                    f"Identified unverified contract: {created_contract_address}"
                                )

                                storage_addresses = get_storage_addresses(
                                    w3, created_contract_address
                                )

                                opcode_addresses = get_opcode_addresses(
                                    w3, created_contract_address
                                )

                                created_contract_addresses.append(
                                    created_contract_address.lower()
                                )

                                FINDINGS_CACHE.append(
                                    UnverifiedCodeContractFindings.unverified_code(
                                        transaction_event.from_,
                                        created_contract_address,
                                        CHAIN_ID,
                                        set.union(storage_addresses, opcode_addresses),
                                        BOT_ID,
                                    )
                                )

                                CREATED_CONTRACTS.pop(created_contract_address)
                            else:
                                logging.info(
                                    f"Identified verified contract: {created_contract_address}"
                                )
                                CREATED_CONTRACTS.pop(created_contract_address, None)

                    for trace in transaction_event.traces:
                        if trace.type == "create":
                            logging.info(
                                f"Contract {created_contract_address} created within trace."
                            )

                            if (
                                transaction_event.from_ == trace.action.from_
                                or trace.action.from_ in created_contract_addresses
                            ):
                                if transaction_event.from_ == trace.action.from_:
                                    nonce = transaction_event.transaction.nonce
                                    calc_created_contract_address = calc_contract_address(w3, trace.action.from_, nonce)
                                else:
                                    # For contracts creating other contracts, get the nonce using Web3
                                    nonce = w3.eth.getTransactionCount(Web3.to_checksum_address(trace.action.from_), transaction_event.block_number)
                                    calc_created_contract_address = calc_contract_address(w3, trace.action.from_, nonce - 1)

                                if (
                                    created_contract_address
                                    == calc_created_contract_address
                                ):
                                    if (
                                        datetime.now()
                                        - datetime.fromtimestamp(
                                            transaction_event.timestamp
                                        )
                                    ) > timedelta(minutes=wait_time):
                                        logging.info(
                                            f"Evaluating contract {created_contract_address} from cache. Is old enough."
                                        )
                                        if not BLOCK_EXPLORER.is_verified(
                                            created_contract_address
                                        ):
                                            logging.info(
                                                f"Identified unverified contract: {created_contract_address}"
                                            )
                                            storage_addresses = get_storage_addresses(
                                                w3, created_contract_address
                                            )

                                            opcode_addresses = get_opcode_addresses(
                                                w3, created_contract_address
                                            )

                                            created_contract_addresses.append(
                                                created_contract_address.lower()
                                            )

                                            FINDINGS_CACHE.append(
                                                UnverifiedCodeContractFindings.unverified_code(
                                                    trace.action.from_,
                                                    created_contract_address,
                                                    CHAIN_ID,
                                                    set.union(
                                                        storage_addresses,
                                                        opcode_addresses,
                                                    ),
                                                    BOT_ID,
                                                )
                                            )
                                            CREATED_CONTRACTS.pop(
                                                created_contract_address, None
                                            )
                                        else:
                                            logging.info(
                                                f"Identified verified contract: {created_contract_address}"
                                            )
                                            CREATED_CONTRACTS.pop(created_contract_address, None)
            if not infinite:
                break

    except Exception:
        logging.warning(traceback.format_exc())


async def handle_transaction(
    transaction_event: forta_bot_sdk.TransactionEvent, provider: AsyncWeb3
) -> list:
    global FINDINGS_CACHE
    global THREAD_STARTED
    if not THREAD_STARTED:
        THREAD_STARTED = True
        thread = threading.Thread(
            target=detect_unverified_contract_creation, args=(provider, BLOCK_EXPLORER)
        )
        thread.start()
    cache_contract_creation(provider, transaction_event)

    # uncomment for local testing; otherwise the process will exit
    # while thread.is_alive():
    #     pass
    findings = FINDINGS_CACHE
    FINDINGS_CACHE = []
    return findings

async def main():
    """This function is the entry point
    """
    await initialize()
    await asyncio.gather(
        scan_ethereum({
            'rpc_url': EVM_RPC,
            'handle_transaction': handle_transaction,
            'rpc_headers': {
                "Content-Type": "application/json"
            }
        }),
        run_health_check()
    )

# only invoke main() if running this file directly (vs importing it for testing)
if __name__ == "__main__":
    asyncio.run(main())