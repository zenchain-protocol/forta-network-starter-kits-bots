VERIFIED_CONTRACT = '0xD56A0d6fe38cD6153C7B26ECE11b405BCADfF253'
UNVERIFIED_CONTRACT = '0x728ad672409DA288cA5B9AA85D1A55b803bA97D7'


class BlockExplorerMock:

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

    def __init__(self, chain_id):
        pass

    def is_verified(self, address):
        if address == VERIFIED_CONTRACT:
            return True
        elif address == UNVERIFIED_CONTRACT:
            return False
        else:
            return False
