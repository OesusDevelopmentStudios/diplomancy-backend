from utils.types import Database
from utils.log import log, Severity

from utils.database.common import (
    create_table,
    execute_query,
    execute_query_and_get,
)

NAME = "users"
SPECS = """
    username varchar(100) NOT NULL,
    username_id SMALLINT CHECK (username_id >= 0 AND username_id <= 9999) NOT NULL,
    email varchar(254) NOT NULL,
    secret BYTEA NOT NULL,
    salt BYTEA NOT NULL,
    token varchar(36),
    valid_since timestamp,
    save_login BOOLEAN DEFAULT FALSE,
    UNIQUE (username, username_id),
    UNIQUE (token),
    CHECK (username <> ''),
    CHECK (email <> ''),
    PRIMARY KEY (email)
"""


class UserFields:
    EMAIL = "email"
    SALT = "salt"
    SAVE_LOGIN = "save_login"
    SECRET = "secret"
    TOKEN = "token"
    USERNAME = "username"
    USERNAME_ID = "username_id"
    VALID_SINCE = "valid_since"


ALL = [UserFields.USERNAME, UserFields.USERNAME_ID, UserFields.EMAIL, UserFields.SECRET, UserFields.SALT,
       UserFields.VALID_SINCE, UserFields.SAVE_LOGIN]


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
        labels = ALL if not filter else filter
        what = "*" if not filter else ", ".join(field for field in filter)
        query = f"""SELECT {what} FROM {NAME} WHERE email = %s;"""

        result = execute_query_and_get(self.db, query, labels, [email])
        if len(result) == 1:
            return result[0]

        return result

    def get_by_username(self, username: str, filter: list[UserFields] = []):
        labels = ALL if not filter else filter
        what = "*" if not filter else ", ".join(field for field in filter)
        query = f"""SELECT {what} FROM {NAME} WHERE username = %s;"""

        result = execute_query_and_get(self.db, query, labels, [username])
        if len(result) == 1:
            return result[0]

        return result

    def get_by_username_id(self, username: str, uid: int, filter: list[UserFields] = []):
        labels = ALL if not filter else filter
        what = "*" if not filter else ", ".join(field for field in filter)
        query = f"""SELECT {what} FROM {NAME} WHERE username = %s AND username_id = %s;"""

        result = execute_query_and_get(self.db, query, labels, [username, uid])
        if len(result) == 1:
            return result[0]

        return result

    def get_by_token(self, token: str, filter: list[UserFields] = []):
        labels = ALL if not filter else filter
        what = "*" if not filter else ", ".join(field for field in filter)
        query = f"""SELECT {what} FROM {NAME} WHERE token = %s"""

        result = execute_query_and_get(self.db, query, labels, [token])
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

    def update_by_email(self, email: str, data: dict):
        what = (" = %s, ".join(key for key in data.keys())) + " = %s"
        values = list(data.values()) + [email]
        query = f"""
            UPDATE {NAME}
            SET {what}
            WHERE email = %s;
        """

        if not execute_query(self.db, query, values):
            log("Update failed", Severity.ERR)
            return False

        return True
