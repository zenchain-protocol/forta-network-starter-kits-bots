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
            self.api_key = secrets_json['apiKeys']['ETHERSCAN_TOKEN']
        elif chain_id == 137:
            self.host = "https://api.polygonscan.com"
            self.api_key = secrets_json['apiKeys']['POLYGONSCAN_TOKEN']
        elif chain_id == 56:
            self.host = "https://api.bscscan.com"
            self.api_key = secrets_json['apiKeys']['BSCSCAN_TOKEN']
        elif chain_id == 42161:
            self.host = "https://api.arbiscan.io"
            self.api_key = secrets_json['apiKeys']['ARBISCAN_TOKEN']
        elif chain_id == 10:
            self.host = "https://api-optimistic.etherscan.io"
            self.api_key = secrets_json['apiKeys']['OPTIMISTICSCAN_TOKEN']
        elif chain_id == 250:
            self.host = "https://api.ftmscan.com"
            self.api_key = secrets_json['apiKeys']['FTMSCAN_TOKEN']
        elif chain_id == 43114:
            self.host = "https://api.snowtrace.io"
            self.api_key = secrets_json['apiKeys']['SNOWTRACE_TOKEN']
        elif chain_id == 8408:
            self.host = "https://zentrace.io/api"
            self.api_key = secrets_json['apiKeys']['ZENTRACE_API_KEY']
        elif chain_id == CHAIN_ID:
            self.host = ARBITRARY_BLOCKSCOUT_ENDPOINT
            self.api_key = secrets_json['apiKeys']['BLOCKSCOUT_TOKEN']

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
