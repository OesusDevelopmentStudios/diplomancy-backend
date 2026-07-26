from utils.types import Database
from utils.log import log, Severity


USER_TABLE = """
    username varchar(100) NOT NULL,
    username_id SMALLINT CHECK (username_id >= 0 AND username_id <= 9999) NOT NULL,
    email varchar(254) NOT NULL,
    password varchar(500) NOT NULL,
    token varchar(500),
    valid_since date,
    UNIQUE (username, username_id),
    PRIMARY KEY (email)
"""


class DBException(Exception):
    """Database Operation exception"""


def _create_table(db: Database, name: str, params: str):
    creation_str = "CREATE TABLE IF NOT EXISTS %s (%s)" % (name, params)
    try:
        db.execute(creation_str)
    except Exception as error:
        log(str(error), Severity.ERR)
        raise DBException('Failed during creation of table "%s"' % name)


def init_database(db: Database) -> bool:
    try:
        _create_table(db, "users", USER_TABLE)
        commit_operation(db)
    except DBException as error:
        log(str(error), Severity.ERR)
        return False

    return True


def commit_operation(db: Database):
    try:
        db.commit()
    except:
        raise DBException("Failed to commit changes")


def execute_query(db, query):
    try:
        result = db.execute(query)
        return result.fetchall()
    except Exception as error:
        log("Invalid query: " + query, Severity.WRN)
        log(str(error), Severity.WRN)

    return []
