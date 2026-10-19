import json
import requests
import os
from config import OPEN5E_API_URL, DOC_KEY, GAME_SYS_KEY, PAGINATION_LIMIT, ROOT_DIR

JSON_DIR = ROOT_DIR / "json_dump"

def get_creature_count():
    creatureURL = f"{OPEN5E_API_URL}creatures/"
    response = requests.get(creatureURL, params={"document__key__iexact": DOC_KEY, "format": "json", "limit": PAGINATION_LIMIT, "fields": "count"})
    response.raise_for_status()
    results = response.json()
    return results["count"]

def get_creatures(pages):
    creatureURL = f"{OPEN5E_API_URL}creatures/"
    for page in range(1, pages + 1):
        response = requests.get(creatureURL, params={"document__key__iexact": DOC_KEY, "format": "json", "limit": PAGINATION_LIMIT, "page": page})
        response.raise_for_status()
        results = response.json()
        with open(f"{ROOT_DIR}/json_dump/creatures{page}.json", "w") as f:
            json.dump(results, f, indent=4)
        print(f"Dumped page {page} of {pages} to json_dump/creatures{page}.json")

def get_sizes():
    sizeURL = f"{OPEN5E_API_URL}sizes/"
    response = requests.get(sizeURL, params={"document__gamesystem__key__iexact": GAME_SYS_KEY, "format": "json"})
    response.raise_for_status()
    results = response.json()
    with open(f"{ROOT_DIR}/json_dump/sizes.json", "w") as f:
        json.dump(results, f, indent=4)
    print(f"Dumped page 1 of 1 to json_dump/sizes.json")   

def get_conditions():
    conditionsURL = f"{OPEN5E_API_URL}conditions/"
    response = requests.get(conditionsURL, params={"document__gamesystem__key__iexact": GAME_SYS_KEY, "format": "json"})
    response.raise_for_status()
    results = response.json()
    with open(f"{ROOT_DIR}/json_dump/conditions.json", "w") as f:
        json.dump(results, f, indent=4)
    print(f"Dumped page 1 of 1 to json_dump/conditions.json")    

def get_environments():
    environmentsURL = f"{OPEN5E_API_URL}environments/"
    response = requests.get(environmentsURL, params={"document__key__in[]": ["core", DOC_KEY], "format": "json"})
    response.raise_for_status()
    results = response.json()
    with open(f"{ROOT_DIR}/json_dump/environments.json", "w") as f:
        json.dump(results, f, indent=4)
    print(f"Dumped page 1 of 1 to json_dump/environments.json")

def get_languages():
    languagesURL = f"{OPEN5E_API_URL}languages/"
    response = requests.get(languagesURL, params={"document__key__iexact": "core", "document__gamesystem__key__iexact":  GAME_SYS_KEY, "format": "json"})
    response.raise_for_status()
    results = response.json()
    with open(f"{ROOT_DIR}/json_dump/languages.json", "w") as f:
        json.dump(results, f, indent=4)
    print(f"Dumped page 1 of 1 to json_dump/languages.json")
    
    
    '''
    The following two endpoints cannot be filtered by game system as the filtering system of the API seems to stop functioning when attempting to apply them to the "descriptions"
    field, and they have no way of filtering by game system outside of the entries in "descriptions". As such, the whole json will be saved and filtering will occur during
    transformations.
    '''
def get_creature_types():
    creaturetypeURL = f"{OPEN5E_API_URL}creaturetypes/"
    response = requests.get(creaturetypeURL, params={"format": "json"})
    response.raise_for_status()
    results = response.json()
    with open(f"{ROOT_DIR}/json_dump/creaturetypes.json", "w") as f:
        json.dump(results, f, indent=4)
    print(f"Dumped page 1 of 1 to json_dump/creaturetypes.json")
    
def get_damage_types():
    damagetypeURL = f"{OPEN5E_API_URL}damagetypes/"
    response = requests.get(damagetypeURL, params={"format": "json"})
    response.raise_for_status()
    results = response.json()
    with open(f"{ROOT_DIR}/json_dump/damagetypes.json", "w") as f:
        json.dump(results, f, indent=4)
    print(f"Dumped page 1 of 1 to json_dump/damagetypes.json")

def main():
    JSON_DIR.mkdir(parents=True, exist_ok=True)
    count = get_creature_count()
    pages = (count // PAGINATION_LIMIT) + (1 if count % PAGINATION_LIMIT > 0 else 0)
    get_creatures(pages)
    get_creature_types()
    get_conditions()
    get_damage_types()
    get_environments()
    get_languages()
    get_sizes()
    
if __name__ == "__main__":
    main()