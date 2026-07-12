from utils.types import Database
from utils.log import log, Severity


USER_TABLE = """
    username varchar(100) NOT NULL,
    email varchar(100) NOT NULL,
    password varchar(500) NOT NULL,
    token varchar(500),
    valid_since date,
    PRIMARY KEY (username)
"""


class DBException(Exception):
    """Database Operation exception"""


def _create_table(db: Database, name: str, params: str):
    creation_str = "CREATE TABLE IF NOT EXISTS %s (%s)" % (name, params)
    try:
        db.execute(creation_str)
    except:
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
