from enum import Enum

from utils.types import Database
from utils.log import log, Severity

from database.helpers.common import (
    create_table,
    execute_query,
    execute_query_and_get
)

NAME = "users"
SPECS = """
    username varchar(100) NOT NULL,
    username_id SMALLINT CHECK (username_id >= 0 AND username_id <= 9999) NOT NULL,
    email varchar(254) NOT NULL,
    secret BYTEA NOT NULL,
    salt BYTEA NOT NULL,
    UNIQUE (username, username_id),
    CHECK (username <> ''),
    CHECK (email <> ''),
    PRIMARY KEY (email)
"""


class Users(Enum):
    EMAIL = "email"
    SALT = "salt"
    SECRET = "secret"
    USERNAME = "username"
    USERNAME_ID = "username_id"


ALL = [Users.USERNAME, Users.USERNAME_ID, Users.EMAIL, Users.SECRET, Users.SALT]


class UserDb:
    def __init__(self, db: Database):
        self.db = db
        self.initilized = create_table(self.db, NAME, SPECS)

    def get_by_email(self, email: str, filter: list[Users] = []):
        labels = ALL if not filter else filter
        what = "*" if not filter else ", ".join(field.value for field in filter)
        query = f"""SELECT {what} FROM {NAME} WHERE email = %s;"""

        result = execute_query_and_get(self.db, query, labels, [email])
        if len(result) == 1:
            return result[0]

        return result

    def get_by_username(self, username: str, filter: list[Users] = []):
        labels = ALL if not filter else filter
        what = "*" if not filter else ", ".join(field.value for field in filter)
        query = f"""SELECT {what} FROM {NAME} WHERE username = %s;"""

        result = execute_query_and_get(self.db, query, labels, [username])
        if len(result) == 1:
            return result[0]

        return result

    def get_by_username_and_id(self, username: str, uid: int, filter: list[Users] = []):
        labels = ALL if not filter else filter
        what = "*" if not filter else ", ".join(field.value for field in filter)
        query = f"""SELECT {what} FROM {NAME} WHERE username = %s AND username_id = %s;"""

        result = execute_query_and_get(self.db, query, labels, [username, uid])
        if len(result) == 1:
            return result[0]

        return result

    def insert(self, username: str, uid: int, email: str, secret: bytes, salt: bytes) -> bool:
        query = f"""
            INSERT INTO {NAME}
                (username, username_id, email, secret, salt)
            VALUES
                (%s, %s, %s, %s, %s);
        """

        if not execute_query(self.db,  query, [username, uid, email, secret, salt]):
            log("Insertion failed", Severity.ERR)
            return False

        return True
