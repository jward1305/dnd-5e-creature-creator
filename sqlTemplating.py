import duckdb
from config import ROOT_DIR

DUCKDB_DIR = ROOT_DIR/"duckdb"/"CreatureCreator.duckdb"
DUCKDB_DIR.parent.mkdir(parents=True, exist_ok=True)
con = duckdb.connect(str(DUCKDB_DIR))

file = ROOT_DIR/"ActionTraitLinking.sql"
sql = file.read_text()
con.execute("DROP TABLE Attacks CASCADE")
con.execute("DROP TABLE CreatureTraits CASCADE")
con.execute("DROP TABLE TraitsFiltered CASCADE")
con.execute(sql)
#con.sql("DESCRIBE Actions").show()
#con.table("Actions").show()
#con.table("Traits").show()
#con.table("CreatureActions").show()
#con.table("Attacks").show()
con.table("TraitsFiltered").show()
con.table("CreatureTraits").show()
con.sql("SELECT ct.CreatureKey FROM CreatureTraits AS ct INNER JOIN TraitsFiltered AS tf ON tf.TraitID = ct.TraitID WHERE tf.TName = 'Amphibious'").show()
con.close()