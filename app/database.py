from pathlib import Path
import sys
from typing import Any

import duckdb

sys.path.insert(1, str(Path(__file__).resolve().parent.parent))

from config import DUCKDB_DIR


def query_database(
    query: str,
    parameters: tuple[Any, ...] = (),
) -> list[tuple[Any, ...]]:
    connection = duckdb.connect(str(DUCKDB_DIR), read_only=True)
    try:
        return connection.execute(query, parameters).fetchall()
    finally:
        connection.close()
