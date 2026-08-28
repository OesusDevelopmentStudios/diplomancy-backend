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
    token varchar(128),
    valid_since date,
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

        result = execute_query_and_get(self.db, query, [email])
        if len(filter) == 1:
            return [value[0] for value in result]

        return result

    def get_by_username(self, username: str, filter: list[UserFields] = []):
        what = "*" if not filter else ", ".join(field for field in filter)
        query = f"""SELECT {what} FROM {NAME} WHERE username = %s;"""

        result = execute_query_and_get(self.db, query, [username])
        if len(filter) == 1:
            return [value[0] for value in result]

        return result

    def get_by_username_id(self, username: str, uid: int, filter: list[UserFields] = []):
        what = "*" if not filter else ", ".join(field for field in filter)
        query = f"""SELECT {what} FROM {NAME} WHERE username = %s AND username_id = %s;"""

        result = execute_query_and_get(self.db, query, [username, uid])
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

        if not execute_query(self.db,  query, [username, uid, email, secret, salt]):
            log("Insertion failed", Severity.ERR)
            return False

        return True

    def set_token_and_expiry(self, email:str, token: str, date: str, save_login: bool) -> bool:
        query = f"""
            UPDATE {NAME}
            SET token = %s, valid_since = %s, save_login = %s
            WHERE email = %s;
        """

        # TODO: Handle date
        if not execute_query(self.db,  query, [token, date, save_login, email]):
            log("Update failed", Severity.ERR)
            return False
        
        return True
