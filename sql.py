import duckdb
import os
from config import ROOT_DIR

DUCKDB_DIR = ROOT_DIR/"duckdb"/"test.duckdb"
DUCKDB_DIR.parent.mkdir(parents=True, exist_ok=True)
con = duckdb.connect(str(DUCKDB_DIR))

#f"SELECT type FROM (SELECT unnest(results, max_depth := 2) FROM read_json('{ROOT_DIR}/json_dump/creatures1.json'))"
#f"SELECT DISTINCT type['name'] FROM (SELECT unnest(results, max_depth := 2) FROM read_json('{ROOT_DIR}/json_dump/creatures1.json'))"
#f"SELECT unnest(results, max_depth := 2) FROM read_json('{ROOT_DIR}/json_dump/creatures1.json')"
#"SELECT type['name'], count(type['name']) FROM firstpass GROUP BY type['name']"
query = f"CREATE TABLE IF NOT EXISTS firstpass AS SELECT unnest(results, max_depth := 2) FROM read_json('{ROOT_DIR}/json_dump/*.json')"
con.sql(query)
con.table("firstpass").show()
query =  "SELECT f1.name, f1.type['name'], f2.typecount FROM firstpass f1 INNER JOIN (SELECT type['name'] AS type, count(type['name']) as typecount FROM firstpass GROUP BY type['name']) f2 ON f1.type['name'] = f2.type"

con.sql(query).show()
con.close()