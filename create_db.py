import duckdb
from config import SQL_DIR, DUCKDB_DIR, JSON_DIR
import attackparsing as ap

def main():
    
    DUCKDB_DIR.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DUCKDB_DIR))
    
    fileCTAS = SQL_DIR / "sqlCTAS.sql"
    sqlCTAS = fileCTAS.read_text()
    sqlCTAS = sqlCTAS.replace("JSON_DIR", str(JSON_DIR))
    
    fileTables = SQL_DIR / "sqlTables.sql"
    sqlTables = fileTables.read_text()
    
    fileParents = SQL_DIR / "sqlParents.sql"
    sqlParents = fileParents.read_text()
    
    fileDependants = SQL_DIR / "sqlDependants.sql"
    sqlDependants = fileDependants.read_text()
        
    con.execute(sqlCTAS)
    con.execute(sqlTables)
    con.execute(sqlParents)
    con.execute(sqlDependants)
    ap.parse_all()
    print("Database Complete.")
    con.sql("SELECT * FROM Attacks").show()

if __name__ == "__main__":
    main()