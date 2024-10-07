import os
import requests
import json
import warnings
from forta_bot_sdk import fetch_jwt
from constants import NODE_ENV, STORAGE_API_URL

# Determine the storage API URL and test mode
test_mode = "production" if NODE_ENV == "production" else "test"

# Function to fetch JWT token
async def _token():
    tk = await fetch_jwt({})
    return {"Authorization": f"Bearer {tk}"}

# Function to fetch individual key values
async def fetch_key(key: str):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    if test_mode == "production":
        token_headers = await _token()
        headers.update(token_headers)
    
    url = f"{STORAGE_API_URL}/value?key={key}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json().get('data', None)
    elif response.status_code == 404:
        warnings.warn(f"Key not found: {key}")
        return None
    else:
        raise ConnectionError(f"Failed to fetch key: {key}, Status: {response.status_code}, Text: {response.text}")

# Function to fetch all secrets
async def get_secrets():
    keys = [
        'ETHERSCAN_API_KEY',
        'POLYGONSCAN_API_KEY',
        'BSCSCAN_API_KEY',
        'ARBISCAN_API_KEY',
        'OPTIMISTICSCAN_API_KEY',
        'FANTOMSCAN_API_KEY',
        'SNOWTRACE_API_KEY',
        'ZETTABLOCK_API_KEY',
        'ZENTRACE_API_KEY'
    ]
    
    api_keys = {}
    all_keys_not_found = True

    for key in keys:
        value = await fetch_key(key)
        if value is not None:
            all_keys_not_found = False
        api_keys[key] = value or ""

    if all_keys_not_found:
        raise ValueError("All keys returned 404. Something is wrong with the key fetching process.")

    return {"apiKeys": api_keys}