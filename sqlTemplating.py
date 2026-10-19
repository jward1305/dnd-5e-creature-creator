import duckdb
from config import ROOT_DIR

DUCKDB_DIR = ROOT_DIR/"duckdb"/"CreatureCreator.duckdb"
DUCKDB_DIR.parent.mkdir(parents=True, exist_ok=True)
con = duckdb.connect(str(DUCKDB_DIR))

ActionQuery = f"CREATE OR REPLACE TABLE Actions AS SELECT key AS CreatureKey, unnest(actions, max_depth := 2) FROM CreaturesRaw"
con.sql(ActionQuery)
con.table("Actions").show()

TraitQuery = f"CREATE OR REPLACE TABLE Traits AS SELECT DISTINCT key AS CreatureKey, unnest(traits, max_depth := 2) FROM CreaturesRaw"
con.sql(TraitQuery)
con.table("Traits").show()


con.close()