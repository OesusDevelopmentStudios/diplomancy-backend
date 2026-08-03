from types import NoneType

from utils.types import Database
from utils.log import log, Severity

from utils.database.common import (
    create_table,
    execute_query
)

NAME = "users"
SPECS = """
    username varchar(100) NOT NULL,
    username_id SMALLINT CHECK (username_id >= 0 AND username_id <= 9999) NOT NULL,
    email varchar(254) NOT NULL,
    secret BYTEA NOT NULL,
    salt BYTEA NOT NULL,
    token BYTEA,
    valid_since date,
    UNIQUE (username, username_id),
    PRIMARY KEY (email)
"""


class UserFields:
    USERNAME = "username"
    USERNAME_ID = "username_id"
    EMAIL = "email"
    SECRET = "secret"
    SALT = "salt"
    TOKEN = "token"
    VALID_SINCE = "valid_since"


class UserTable:
    def __init__(self, db: Database):
        self.db = db

        try:
            create_table(self.db, NAME, SPECS)
            self.db.commit()
            self.initilized = True
        except Exception as error:
            log("Failed to initilize database", Severity.ERR)
            log(str(error))
            db.rollback()
            self.initilized = False

    def is_initilized(self):
        return self.initilized

    def get_by_email(self, email: str, filter: list[UserFields] = []):
        what = "*" if not filter else ", ".join(field for field in filter)
        query = f"""SELECT {what} FROM {NAME} WHERE email = %s;"""

        result = execute_query(self.db, query, (email))
        if len(filter) == 1:
            return [value[0] for value in result]

        return result

    def get_by_username(self, username: str, filter: list[UserFields] = []):
        what = "*" if not filter else ", ".join(field for field in filter)
        query = f"""SELECT {what} FROM {NAME} WHERE username = %s;"""

        result = execute_query(self.db, query, (username))
        if len(filter) == 1:
            return [value[0] for value in result]

        return result

    def insert(self, username: str, uid: int, email: str, secret: bytes, salt: bytes) -> bool:
        query = f"""
            INSERT INTO {NAME}
                (username, username_id, email, secret, salt)
            VALUES
                (%s, %s, %s, %s, %s);
        """

        try:
            self.db.execute(query, (username, uid, email, secret, salt))
            self.db.commit()
        except Exception as error:
            log("Insertion failed: " + query, Severity.ERR)
            log(error, Severity.ERR)
            self.db.rollback()
            return False

        return True
