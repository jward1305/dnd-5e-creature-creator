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
    print("sqlCTAS Complete.")
    con.execute(sqlTables)
    print("sqlTables Complete.")
    con.execute(sqlParents)
    print("sqlParents Complete.")
    con.execute(sqlDependants)
    print("sqlDependants Complete.")
    ap.parse_all()
    print("Attack Parsing Complete.")
    print("Database Complete.")

if __name__ == "__main__":
    main()