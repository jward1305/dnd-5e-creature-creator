import duckdb
from config import ROOT_DIR

DUCKDB_DIR = ROOT_DIR/"duckdb"/"CreatureCreator.duckdb"
DUCKDB_DIR.parent.mkdir(parents=True, exist_ok=True)
con = duckdb.connect(str(DUCKDB_DIR))
#(2 + floor((challenge_rating - 1) / 4)
file = ROOT_DIR/"sqlTyping.sql"
sql = file.read_text()
con.execute(sql)
con.table("CreaturesTyped").show()
#con.sql("SELECT CreatureName, Str, Dex, Con, Int, Wis, Cha FROM CreaturesTyped").show()



con.close()