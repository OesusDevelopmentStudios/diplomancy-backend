from utils.types import Database
from utils.log import log, Severity


def _adapt_values(labels: list[str], values: any) -> list:
    data = []
    for row in values:
        dict = {}
        for label, value in zip(labels, row):
            dict[label] = value

        data.append(dict)

    return data



def create_table(db: Database, name: str, params: str):
    creation_str = "CREATE TABLE IF NOT EXISTS %s (%s)" % (name, params)
    db.execute(creation_str)


def execute_query(db: Database, query, params: list) -> bool:
    try:
        db.execute(query, params)
        db.commit()
        return True
    except Exception as error:
        log("Invalid query: " + query, Severity.WRN)
        log(str(error), Severity.WRN)
        db.rollback()

    return False


def execute_query_and_get(db: Database, query: str, labels: list[str], params: list) -> list:
    try:
        result = db.execute(query, params)
        values = result.fetchall()
        db.commit()
        return _adapt_values(labels, values)
    except Exception as error:
        log("Invalid query: " + query, Severity.WRN)
        log(str(error), Severity.WRN)
        db.rollback()

    return []
