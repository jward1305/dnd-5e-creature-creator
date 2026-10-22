import os
from pathlib import Path


OPEN5E_API_URL = "https://api.open5e.com/v2/"
PAGINATION_LIMIT = 50
DOC_KEY = "srd-2014"
GAME_SYS_KEY = "5e-2014"

ROOT_DIR = Path(__file__).resolve().parent
DUCKDB_DIR = ROOT_DIR/"duckdb"/"CreatureCreator.duckdb"
SQL_DIR = ROOT_DIR / "sql"
JSON_DIR = ROOT_DIR / "json_dump"