import duckdb
from config import ROOT_DIR

DUCKDB_DIR = ROOT_DIR/"duckdb"/"CreatureCreator.duckdb"
DUCKDB_DIR.parent.mkdir(parents=True, exist_ok=True)
con = duckdb.connect(str(DUCKDB_DIR))
file = ROOT_DIR/"sqlStructure.sql"
sql = file.read_text()
con.execute(sql)
con.table("CreaturesStructured").show()
con.table("CreatureTypesStructured").show()
con.table("ConditionsStructured").show()
con.table("DamageTypesStructured").show()
con.table("EnvironmentsStructured").show()
con.table("LanguagesStructured").show()
con.table("SizesStructured").show()
#con.sql("SELECT CreatureName, Str, Dex, Con, Int, Wis, Cha FROM CreaturesStructured").show()



con.close()