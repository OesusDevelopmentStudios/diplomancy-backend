import datetime

from types import NoneType
from uuid import uuid4

from utils.http import Response
from utils.database.users import UserTable

from auth.helpers import (
    get_next_uid,
    get_user_data,
    get_uuid,
    hash_password,
    validate_password,
    verify_password
)


class Reason:
    BAD_PASSWORD = 0
    BAD_USERNAME = 1
    BAD_EMAIL = 2
    BAD_USER_ID = 3
    MISSING_REMEMBER_VALUE = 4


class AuthResponse:
    def __init__(self, response: Response, username: str|NoneType = None, detail: list[Reason]|NoneType = None,
                 token: str|NoneType = None):
        self.response = response
        self.username = username
        self.detail = detail
        self.token = token

    def code(self):
        return self.response.value

    def dict(self):
        dict = {}
        if self.username:
            dict["username"] = self.username

        if self.detail:
            dict["detail"] = self.detail

        if self.token:
            dict["token"] = self.token

        return dict


def handle_logon(
        user_db: UserTable, email: str|NoneType, username: str|NoneType, password: str|NoneType) -> AuthResponse:
    if not email or not username or not password:
        reason = []
        if not email: reason.append(Reason.BAD_EMAIL)
        if not username: reason.append(Reason.BAD_USERNAME)
        if not password: reason.append(Reason.BAD_PASSWORD)
        return AuthResponse(Response.BAD_REQUEST, detail=reason)

    if "#" in username:
        return AuthResponse(Response.BAD_REQUEST, detail=[Reason.BAD_USERNAME])

    if not validate_password(password):
        return AuthResponse(Response.BAD_REQUEST, detail=[Reason.BAD_PASSWORD])

    if user_db.get_by_email(email):
        return AuthResponse(Response.CONFLICT)

    uid = get_next_uid(user_db, username)
    salt, secret = hash_password(password)
    success = user_db.insert(username, uid, email, secret, salt)
    if not success:
        return AuthResponse(Response.INTERNAL_SERVER_ERROR)

    return AuthResponse(Response.CREATED, username=get_uuid(username, uid))


def handle_login(
        user_db: UserTable, user_id: str|NoneType, password: str|NoneType, remember: bool|NoneType) -> AuthResponse:
    if not user_id or not password or remember is NoneType:
        reason = []
        if not user_id: reason.append(Reason.BAD_USER_ID)
        if not password: reason.append(Reason.BAD_PASSWORD)
        if remember is NoneType: reason.append(Reason.MISSING_REMEMBER_VALUE)
        return AuthResponse(Response.BAD_REQUEST, detail=reason)

    user_data = get_user_data(user_db, user_id)
    if not user_data:
        return AuthResponse(Response.NOT_FOUND)

    if len(user_data) != 1:
        return AuthResponse(Response.INTERNAL_SERVER_ERROR)

    email, salt, secret = user_data[0]
    if not verify_password(salt, secret, password):
        return AuthResponse(Response.UNAUTHORIZED)

    token = uuid4()
    if not user_db.set_token_and_expiry(email, str(token), str(datetime.datetime.now()), remember):
        return AuthResponse(Response.INTERNAL_SERVER_ERROR)

    return AuthResponse(Response.OK, token=token)
