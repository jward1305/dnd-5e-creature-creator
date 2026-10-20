import duckdb
from config import ROOT_DIR

DUCKDB_DIR = ROOT_DIR/"duckdb"/"CreatureCreator.duckdb"
DUCKDB_DIR.parent.mkdir(parents=True, exist_ok=True)
con = duckdb.connect(str(DUCKDB_DIR))
file = ROOT_DIR/"sqlLinking.sql"
sql = file.read_text()
con.execute(sql)

#con.table("CreatureLanguages").show()
#con.table("CreatureEnvironments").show()
#con.table("CreatureConditionImmunities").show()
#con.table("CreatureDamageRelationships").show()
con.sql("SELECT CreatureKey, 'save' AS kind, * EXCLUDE (CreatureKey) FROM CreatureSaveProficiencies WHERE list_min([Str_Prof, Dex_Prof, Con_Prof, Int_Prof, Wis_Prof, Cha_Prof]) < 0 OR list_max([Str_Prof, Dex_Prof, Con_Prof, Int_Prof, Wis_Prof, Cha_Prof]) > 2;").show()
con.close()