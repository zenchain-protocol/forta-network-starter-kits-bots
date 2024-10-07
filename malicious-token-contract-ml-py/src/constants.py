from os import environ
from dotenv import load_dotenv

load_dotenv()

CONTRACT_SLOT_ANALYSIS_DEPTH = 20  # how many slots should be read to extract contract addresses from created contract

MODEL_THRESHOLD = 0.5  # threshold for model prediction
SAFE_CONTRACT_THRESHOLD = 0.1  # threshold for labelling safe contract
BYTE_CODE_LENGTH_THRESHOLD = (
    60  # ignore contracts with byte code length below this threshold
)
MASK = "0xffffffffffffffffffffffffffffffffffffffff"

CHAIN_ID = int(environ['CHAIN_ID'])
EVM_RPC = environ['EVM_RPC']
NODE_ENV = environ['NODE_ENV']
STORAGE_API_URL = environ['STORAGE_API_URL']