import os

OPEN5E_API_URL = "https://api.open5e.com/v2/"
PAGINATION_LIMIT = 50
DOC_KEY = "srd-2014"

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(f"{ROOT_DIR}/json_dump", exist_ok=True)