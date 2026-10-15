import json
import requests
from config import OPEN5E_API_URL, DOC_KEY, PAGINATION_LIMIT, ROOT_DIR

creatureURL = OPEN5E_API_URL + "creatures/"

def get_count():
    response = requests.get(creatureURL, params={"document__key__iexact": DOC_KEY, "format": "json", "limit": PAGINATION_LIMIT, "fields": "count"})
    response.raise_for_status()
    results = response.json()
    return results["count"]

def main():
    count = get_count()
    pages = (count // PAGINATION_LIMIT) + (1 if count % PAGINATION_LIMIT > 0 else 0)
    for page in range(1, pages + 1):
        response = requests.get(creatureURL, params={"document__key__iexact": DOC_KEY, "format": "json", "limit": PAGINATION_LIMIT, "page": page})
        response.raise_for_status()
        results = response.json()
        with open(f"{ROOT_DIR}/json_dump/creatures{page}.json", "w") as f:
            json.dump(results, f, indent=4)
        print(f"Dumped page {page} of {pages} to json_dump/creatures{page}.json")