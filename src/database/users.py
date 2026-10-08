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
    email varchar(254) NOT NULL,
    name_id SMALLINT CHECK (name_id >= 0 AND name_id <= 9999) NOT NULL,
    salt BYTEA NOT NULL,
    secret BYTEA NOT NULL,
    username varchar(100) NOT NULL,
    uuid varchar(10) NOT NULL,
    UNIQUE (username, name_id),
    CHECK (username <> ''),
    CHECK (email <> ''),
    PRIMARY KEY (uuid)
"""


class Users(Enum):
    EMAIL = "email"
    NAME_ID = "name_id"
    SALT = "salt"
    SECRET = "secret"
    USERNAME = "username"
    UUID = "UUID"


ALL = [Users.EMAIL, Users.NAME_ID, Users.SALT, Users.SECRET, Users.USERNAME, Users.UUID]


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

    def get_by_username_with_id(self, username: str, name_id: int, filter: list[Users] = []):
        labels = ALL if not filter else filter
        what = "*" if not filter else ", ".join(field.value for field in filter)
        query = f"""SELECT {what} FROM {NAME} WHERE username = %s AND name_id = %s;"""

        result = execute_query_and_get(self.db, query, labels, [username, name_id])
        if len(result) == 1:
            return result[0]

        return result

    def get_by_uuid(self, uuid, filter: list[Users] = []):
        labels = ALL if not filter else filter
        what = "*" if not filter else ", ".join(field.value for field in filter)
        query = f"""SELECT {what} FROM {NAME} WHERE uuid = %s;"""

        result = execute_query_and_get(self.db, query, labels, [uuid])
        if len(result) == 1:
            return result[0]

        return result

    def insert(self, email: str, name_id: int, salt: bytes, secret: bytes, username: str, uuid: str) -> bool:
        query = f"""
            INSERT INTO {NAME}
                (email, name_id, salt, secret, username, uuid)
            VALUES
                (%s, %s, %s, %s, %s, %s);
        """

        if not execute_query(self.db,  query, [email, name_id, salt, secret, username, uuid]):
            log("Insertion failed", Severity.ERR)
            return False

        return True
