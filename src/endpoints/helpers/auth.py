import os
import re
import hashlib
import hmac

from datetime import datetime
from types import NoneType
from uuid import uuid4

from database.users import UserDb, Users
from database.sessions import SessionDb, Sessions

from endpoints.helpers.common.http import Response
from endpoints.helpers.common.utils import get_session_if_valid


def _get_sorted_ids(user_db: UserDb, username: str):
    result = user_db.get_by_username(username, [Users.USERNAME_ID])
    if not result:
        return []

    if isinstance(result, dict):
        return [result[Users.USERNAME_ID]]

    return sorted([id[Users.USERNAME_ID] for id in result])


def _validate_password(password: str) -> bool:
    return re.match(r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$', password)


def _hash_password(password: str) -> tuple[bytes, bytes]:
    salt = os.urandom(16)
    secret = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 1000000)
    return salt, secret


def _verify_password(salt: bytes, secret: str, password: str) -> bool:
    return hmac.compare_digest(secret, hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 1000000))


def _get_next_uid(user_db: UserDb, username: str) -> int:
    new_id = 0
    ids = _get_sorted_ids(user_db, username)
    for taken_id in ids:
        if taken_id > new_id:
            return new_id
        if new_id == taken_id:
            new_id = new_id + 1

    return new_id


def _get_uuid(username: str, uid: int) -> str:
    zeros = 4 - len(str(uid))
    return username + "#" + zeros * "0" + str(uid)


def _get_user_data(user_db: UserDb, user_id: str):
    if "#" in user_id:
        username, uid = user_id.split("#")
        if len(uid) != 4 or not uid.isdigit():
            return None

        return user_db.get_by_username_and_id(username, int(uid), [
            Users.USERNAME, Users.USERNAME_ID, Users.EMAIL, Users.SALT, Users.SECRET])
    else:
        return user_db.get_by_email(user_id, [
            Users.USERNAME, Users.USERNAME_ID, Users.EMAIL, Users.SALT, Users.SECRET])


def _get_unique_token(session_db: SessionDb) -> str:
    while True:
        token = uuid4()
        if not get_session_if_valid(session_db, token=str(token)):
            return str(token)


class Reason:
    BAD_PASSWORD = 0
    BAD_USERNAME = 1
    BAD_EMAIL = 2
    BAD_USER_ID = 3
    MISSING_TOKEN_VALUE = 4


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


def handle_logon(user_db: UserDb, email: str|NoneType, username: str|NoneType, password: str|NoneType) -> AuthResponse:
    if not email or not username or not password:
        reason = []
        if not email: reason.append(Reason.BAD_EMAIL)
        if not username: reason.append(Reason.BAD_USERNAME)
        if not password: reason.append(Reason.BAD_PASSWORD)
        return AuthResponse(Response.BAD_REQUEST, detail=reason)

    if "#" in username:
        return AuthResponse(Response.BAD_REQUEST, detail=[Reason.BAD_USERNAME])

    if not _validate_password(password):
        return AuthResponse(Response.BAD_REQUEST, detail=[Reason.BAD_PASSWORD])

    if user_db.get_by_email(email):
        return AuthResponse(Response.CONFLICT)

    uid = _get_next_uid(user_db, username)
    salt, secret = _hash_password(password)
    success = user_db.insert(username, uid, email, secret, salt)
    if not success:
        return AuthResponse(Response.INTERNAL_SERVER_ERROR)

    return AuthResponse(Response.CREATED, username=_get_uuid(username, uid))


def handle_login(user_db: UserDb, session_db: SessionDb, user_id: str|NoneType, password: str|NoneType,
                 store_session: bool) -> AuthResponse:
    if not user_id or not password:
        reason = []
        if not user_id: reason.append(Reason.BAD_USER_ID)
        if not password: reason.append(Reason.BAD_PASSWORD)
        return AuthResponse(Response.BAD_REQUEST, detail=reason)

    user = _get_user_data(user_db, user_id)
    if not user:
        return AuthResponse(Response.NOT_FOUND)

    if not isinstance(user, dict):
        return AuthResponse(Response.INTERNAL_SERVER_ERROR)

    username = user[Users.USERNAME]
    uid = user[Users.USERNAME_ID]
    email = user[Users.EMAIL]
    salt = user[Users.SALT]
    secret = user[Users.SECRET]
    if not _verify_password(salt, secret, password):
        return AuthResponse(Response.UNAUTHORIZED)

    session = get_session_if_valid(session_db, email=email)
    if isinstance(session, dict):
        session_db.remove(session[Sessions.TOKEN])

    token = _get_unique_token(session_db)
    if not session_db.insert(token, str(datetime.now()), store_session, email):
        return AuthResponse(Response.INTERNAL_SERVER_ERROR)

    return AuthResponse(Response.OK, token=token, username=_get_uuid(username, uid))


def handle_validate(user_db: UserDb, session_db: SessionDb, token: str|NoneType) -> AuthResponse:
    if not token:
        return AuthResponse(Response.BAD_REQUEST, detail=[Reason.MISSING_TOKEN_VALUE])

    session = get_session_if_valid(session_db, token=token)
    if not isinstance(session, dict):
        return AuthResponse(Response.UNAUTHORIZED)

    user = user_db.get_by_email(session[Sessions.EMAIL], [Users.USERNAME, Users.USERNAME_ID])
    if not isinstance(user, dict):
        session_db.remove(token)
        return AuthResponse(Response.NOT_FOUND)

    username = user[Users.USERNAME]
    uid = user[Users.USERNAME_ID]

    return AuthResponse(Response.OK, username=_get_uuid(username, uid))


def handle_logout(session_db: SessionDb, token: str|NoneType) -> AuthResponse:
    if not token:
        return AuthResponse(Response.BAD_REQUEST, detail=[Reason.MISSING_TOKEN_VALUE])

    session = get_session_if_valid(session_db, token=token)
    if not isinstance(session, dict):
        return AuthResponse(Response.OK)

    if not session_db.remove(token):
        return AuthResponse(Response.INTERNAL_SERVER_ERROR)

    return AuthResponse(Response.OK)
