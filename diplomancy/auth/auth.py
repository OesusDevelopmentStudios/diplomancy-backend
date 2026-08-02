from types import NoneType

from utils.http import Response
from utils.database.users import UserTable

from auth.helpers import (
    get_next_uid,
    get_uuid,
    hash_password,
    validate_password
)


class Reason:
    BAD_PASSWORD = 0
    BAD_USERNAME = 1
    BAD_EMAIL = 2


class AuthResponse:
    def __init__(self, response: Response, username: str|NoneType = None, detail: list[Reason]|NoneType = None):
        self.response = response
        self.username = username
        self.detail = detail

    def code(self):
        return self.response.value

    def username(self):
        return self.username

    def dict(self):
        dict = {}
        if self.username:
            dict["username"] = self.username

        if self.detail:
            dict["detail"] = self.detail

        return dict


def handle_logon(user_db: UserTable, email: str|NoneType, username: str|NoneType, password: str|NoneType) -> AuthResponse:
    if email is None or username is None or password is None:
        reason = []
        if email is None: reason.append(Reason.BAD_EMAIL)
        if username is None: reason.append(Reason.BAD_USERNAME)
        if password is None: reason.append(Reason.BAD_PASSWORD)
        return AuthResponse(Response.BAD_REQUEST, detail=reason)

    if not validate_password(password):
        return AuthResponse(Response.BAD_REQUEST, [Reason.BAD_PASSWORD])

    if user_db.get_by_email(email):
        return AuthResponse(Response.CONFLICT)

    uid = get_next_uid(user_db, username)
    salt, secret = hash_password(password)
    success = user_db.insert(username, uid, email, secret, salt)
    if not success:
        return AuthResponse(Response.INTERNAL_SERVER_ERROR)

    return AuthResponse(Response.CREATED, get_uuid(username, uid))
