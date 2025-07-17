import requests

def download(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()