import os
from dotenv import load_dotenv

load_dotenv()

CONTRACT_SLOT_ANALYSIS_DEPTH = 20  # how many slots should be read to extract contract addresses from created contract
WAIT_TIME = 30  # how many minutes after contract creation we will wait for the creator to share source code on etherscan
CONCURRENT_SIZE = 5  # how many concurrent connections should be made.
ARBITRARY_BLOCKSCOUT_ENDPOINT = os.environ["ARBITRARY_BLOCKSCOUT_ENDPOINT"]
BOT_ID = os.environ["FORTA_BOT_ID"]
CHAIN_ID = int(os.environ["FORTA_CHAIN_ID"])
EVM_RPC = os.environ["EVM_RPC"]
NODE_ENV = os.environ["NODE_ENV"]
STORAGE_API_URL = os.environ["STORAGE_API_URL"]