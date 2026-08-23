from utils.types import Database
from utils.log import log, Severity


def create_table(db: Database, name: str, params: str):
    creation_str = "CREATE TABLE IF NOT EXISTS %s (%s)" % (name, params)
    db.execute(creation_str)


def execute_query(db: Database, query, params: list):
    try:
        result = db.execute(query, params)
        values = result.fetchall()
        db.commit()
        return values
    except Exception as error:
        log("Invalid query: " + query, Severity.WRN)
        log(str(error), Severity.WRN)
        db.rollback()

    return []
