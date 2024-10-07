VERIFIED_CONTRACT = '0xD56A0d6fe38cD6153C7B26ECE11b405BCADfF253'
UNVERIFIED_CONTRACT = '0x728ad672409DA288cA5B9AA85D1A55b803bA97D7'


class BlockExplorerMock:

    SECRETS_JSON = {
        "apiKeys": {
            "ETHERSCAN_API_KEY": "your-etherscan-api-key",
            "POLYGONSCAN_API_KEY": "your-polygonscan-api-key",
            "BSCSCAN_API_KEY": "your-bscscan-api-key",
            "ARBISCAN_API_KEY": "your-arbiscan-api-key",
            "OPTIMISTICSCAN_API_KEY": "your-optimisticscan-api-key",
            "FTMSCAN_API_KEY": "your-ftmscan-api-key",
            "SNOWTRACE_API_KEY": "your-snowtrace-api-key",
            "BLOCKSCOUT_API_KEY": "your-blockscout-api-key",
            "ZETTABLOCK_API_KEY": "your-zettablock-api-key",
            "ZENTRACE_API_KEY": "your-zentrace-api-key",
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
