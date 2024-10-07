import json
import logging
import asyncio

import requests
from functools import lru_cache
from storage import get_secrets
from constants import ARBITRARY_BLOCKSCOUT_ENDPOINT, CHAIN_ID

class BlockExplorer:
    api_key = ""
    host = ""

    def __init__(self, chain_id, secrets_json):
        if chain_id == 1:
            self.host = "https://api.etherscan.io"
            self.api_key = secrets_json['apiKeys']['ETHERSCAN_API_KEY']
        elif chain_id == 137:
            self.host = "https://api.polygonscan.com"
            self.api_key = secrets_json['apiKeys']['POLYGONSCAN_API_KEY']
        elif chain_id == 56:
            self.host = "https://api.bscscan.com"
            self.api_key = secrets_json['apiKeys']['BSCSCAN_API_KEY']
        elif chain_id == 42161:
            self.host = "https://api.arbiscan.io"
            self.api_key = secrets_json['apiKeys']['ARBISCAN_API_KEY']
        elif chain_id == 10:
            self.host = "https://api-optimistic.etherscan.io"
            self.api_key = secrets_json['apiKeys']['OPTIMISTICSCAN_API_KEY']
        elif chain_id == 250:
            self.host = "https://api.ftmscan.com"
            self.api_key = secrets_json['apiKeys']['FANTOMSCAN_API_KEY']
        elif chain_id == 43114:
            self.host = "https://api.snowtrace.io"
            self.api_key = secrets_json['apiKeys']['SNOWTRACE`_API_KEY`']
        elif chain_id == 8408:
            self.host = "https://zentrace.io/api"
            self.api_key = secrets_json['apiKeys']['ZENTRACE_API_KEY']
        else:
            raise ValueError("Unknown Network")

    @lru_cache(maxsize=100)
    def is_verified(self, address):
        url = self.host + "/api?module=contract&action=getabi&address=" + address + "&apikey=" + self.api_key
        response = requests.get(url)
        if (response.status_code == 200):
            data = json.loads(response.text)
            if data['status'] == '1':
                return True
        else:
            logging.warn("Unable to check if contract is verified. Etherscan returned status code " + str(response.status_code))

        return False
