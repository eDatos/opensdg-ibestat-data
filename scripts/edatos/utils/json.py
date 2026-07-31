import os

import requests


def download(url):
    api_key = os.environ.get("ODS_LOAD_API_KEY")
    response = requests.get(url, headers={"api-key": api_key} if api_key else None)
    response.raise_for_status()
    return response.json()
