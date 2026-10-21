import duckdb
from config import ROOT_DIR
import attackparsing as ap

def main():
    DUCKDB_DIR = ROOT_DIR/"duckdb"/"CreatureCreator.duckdb"
    DUCKDB_DIR.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DUCKDB_DIR))
    
    #Transforms raw json data into SQL. 
    #creatures*.json: Each Creature has a single row populated by unnested results array.
    #conditions.json: Each Condition has a single row populated by unnested results array. Stores descriptions as a Structure
    #                   as irrelevant results have not been filtered out yet.
    #creaturetypes.json: Each Creature Type has a single row populated by unnested results array. Stores descriptions as a Structure
    #                   as irrelevant results have not been filtered out yet.
    #damagetypes.json: Each Damage Type has a single row populated by unnested results array. Stores descriptions as a Structure
    #                   as irrelevant results have not been filtered out yet.
    #environments.json: Each Environment has a single row populated by unnested results array.
    #languages.json: Each Language has a single row populated by unnested results array.
    #sizes.json: Each Size category has a single row populated by unnested results array.
    fileRaw = ROOT_DIR/"sqlRaw.sql"
    sqlRaw = fileRaw.read_text()
    sqlRaw = sqlRaw.replace("{ROOT_DIR}", str(ROOT_DIR))
    con.execute(sqlRaw)
    
    #Creates tables with correctly typed, filtered, and constrained fields and inserts data from previous tables
    #The data for conditions, creature types, and damage types is filtered to the correct gamesystem
    fileStructuring = ROOT_DIR/"sqlStructure.sql"
    sqlStructuring = fileStructuring.read_text()
    con.execute(sqlStructuring)

    #Creates linking tables to handle various many-to-many relationships that creatures have with other data.
    #Also creates subtables to store creature proficiencies rather than calculating the values so users can edit them seperately
    fileLinking = ROOT_DIR/"sqlLinking.sql"
    sqlLinking = fileLinking.read_text()
    con.execute(sqlLinking)
    
    #Creates tables
    file = ROOT_DIR/"ActionTraitLinking.sql"
    sql = file.read_text()
    #con.execute("DROP TABLE Attacks CASCADE")
    con.execute(sql)
    ap.main()

if __name__ == "__main__":
    main()