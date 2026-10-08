from enum import Enum

from utils.types import Database
from utils.log import log, Severity

from database.helpers.common import (
    create_table,
    execute_query,
    execute_query_and_get
)


NAME = "sessions"
SPECS = """
    token varchar(36) NOT NULL,
    start timestamp NOT NULL,
    store_session BOOLEAN DEFAULT FALSE,
    email varchar(254) NOT NULL,
    UNIQUE (email),
    PRIMARY KEY (token)
"""

# TODO: ID WITH UUID instead of email, do not make email uniqe (Support of more thank one loggged in session (Future goal))
class Sessions(Enum):
    TOKEN = "token"
    START = "start"
    STORE_SESSION = "store_session"
    EMAIL = "email"


ALL = [Sessions.TOKEN, Sessions.START, Sessions.STORE_SESSION, Sessions.EMAIL]


class SessionDb:
    def __init__(self, db: Database):
        self.db = db
        self.initilized = create_table(self.db, NAME, SPECS)

    def get_by_token(self, token: str, filter: list[Sessions] = []):
        labels = ALL if not filter else filter
        what = "*" if not filter else ", ".join(field.value for field in filter)
        query = f"""SELECT {what} FROM {NAME} WHERE token = %s;"""

        result = execute_query_and_get(self.db, query, labels, [token])
        if len(result) == 1:
            return result[0]

        return result

    def get_by_email(self, email: str, filter: list[Sessions] = []):
        labels = ALL if not filter else filter
        what = "*" if not filter else ", ".join(field.value for field in filter)
        query = f"""SELECT {what} FROM {NAME} WHERE email = %s;"""

        result = execute_query_and_get(self.db, query, labels, [email])
        if len(result) == 1:
            return result[0]

        return result

    def insert(self, token: str, start: str, store_session: bool, email: str) -> bool:
        query = f"""
            INSERT INTO {NAME}
                (token, start, store_session, email)
            VALUES
                (%s, %s, %s, %s)
        """

        if not execute_query(self.db, query, [token, start, store_session, email]):
            log("Insertion failed", Severity.ERR)
            return False

        return True

    def remove(self, token) -> bool:
        query = f"""DELETE FROM {NAME} WHERE token = %s"""
        if not execute_query(self.db, query, [token]):
            log("Deletion failed", Severity.ERR)
            return False

        return True
