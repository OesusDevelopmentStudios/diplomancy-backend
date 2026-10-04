import os
import re
import hashlib
import hmac

from datetime import datetime
from types import NoneType
from uuid import uuid4

from database.users import UserDb, UserFields

from endpoints.helpers.common.http import Response


def _get_data_by_username(user_db: UserDb, uuid: str):
    username, uid = uuid.split("#")
    if len(uid) != 4 or not uid.isdigit():
        return None

    return user_db.get_by_username_id(username, int(uid), [
        UserFields.USERNAME, UserFields.USERNAME_ID, UserFields.EMAIL, UserFields.SALT, UserFields.SECRET])


def _get_sorted_ids(user_db: UserDb, username: str):
    result = user_db.get_by_username(username, [UserFields.USERNAME_ID])
    if not result:
        return []

    if isinstance(result, dict):
        return [result[UserFields.USERNAME_ID]]

    return sorted([id[UserFields.USERNAME_ID] for id in result])


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
        return _get_data_by_username(user_db, user_id)
    else:
        return user_db.get_by_email(user_id, [
            UserFields.USERNAME, UserFields.USERNAME_ID, UserFields.EMAIL, UserFields.SALT, UserFields.SECRET])


def _is_token_valid(user_db: UserDb, token: str):
    data = user_db.get_by_token(token, [UserFields.VALID_SINCE, UserFields.SAVE_LOGIN])
    if not isinstance(data, dict):
        return False

    valid_since = data[UserFields.VALID_SINCE]
    save_login = data[UserFields.SAVE_LOGIN]
    diff = datetime.now() - valid_since
    if save_login and diff.days > 30:
        return False

    if not save_login and diff.days > 1:
        return False

    return True


def _get_unique_token(user_db) -> str:
    while True:
        token = uuid4()
        if not _is_token_valid(user_db, str(token)):
            return str(token)


class Reason:
    BAD_PASSWORD = 0
    BAD_USERNAME = 1
    BAD_EMAIL = 2
    BAD_USER_ID = 3
    MISSING_REMEMBER_VALUE = 4
    MISSING_TOKEN_VALUE = 5


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
        user_db: UserDb, email: str|NoneType, username: str|NoneType, password: str|NoneType) -> AuthResponse:
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


def handle_login(
        user_db: UserDb, user_id: str|NoneType, password: str|NoneType, remember: bool|NoneType) -> AuthResponse:
    if not user_id or not password or remember is NoneType:
        reason = []
        if not user_id: reason.append(Reason.BAD_USER_ID)
        if not password: reason.append(Reason.BAD_PASSWORD)
        if remember is NoneType: reason.append(Reason.MISSING_REMEMBER_VALUE)
        return AuthResponse(Response.BAD_REQUEST, detail=reason)

    user_data = _get_user_data(user_db, user_id)
    if not user_data:
        return AuthResponse(Response.NOT_FOUND)

    if not isinstance(user_data, dict):
        return AuthResponse(Response.INTERNAL_SERVER_ERROR)

    username = user_data[UserFields.USERNAME]
    uid = user_data[UserFields.USERNAME_ID]
    email = user_data[UserFields.EMAIL]
    salt = user_data[UserFields.SALT]
    secret = user_data[UserFields.SECRET]
    if not _verify_password(salt, secret, password):
        return AuthResponse(Response.UNAUTHORIZED)

    token = _get_unique_token(user_db)
    success = user_db.update_by_email(email, {
        UserFields.TOKEN: token,
        UserFields.VALID_SINCE: str(datetime.now()),
        UserFields.SAVE_LOGIN: remember})
    if not success:
        return AuthResponse(Response.INTERNAL_SERVER_ERROR)

    return AuthResponse(Response.OK, token=token, username=_get_uuid(username, uid))


def handle_validate(user_db: UserDb, token: str|NoneType) -> AuthResponse:
    if not token:
        return AuthResponse(Response.BAD_REQUEST, detail=[Reason.MISSING_TOKEN_VALUE])

    data = user_db.get_by_token(token, [UserFields.USERNAME, UserFields.USERNAME_ID])
    if not isinstance(data, dict):
        return AuthResponse(Response.UNAUTHORIZED)

    username = data[UserFields.USERNAME]
    uid = data[UserFields.USERNAME_ID]

    return AuthResponse(Response.OK, username=_get_uuid(username, uid))


def handle_logout(user_db: UserDb, token: str|NoneType) -> AuthResponse:
    if not token:
        return AuthResponse(Response.BAD_REQUEST, detail=[Reason.MISSING_TOKEN_VALUE])

    data = user_db.get_by_token(token, [UserFields.EMAIL])
    if not data:
        return AuthResponse(Response.NOT_FOUND)

    email = data[UserFields.EMAIL]
    success = user_db.update_by_email(email, {
        UserFields.TOKEN: None,
        UserFields.VALID_SINCE: None,
        UserFields.SAVE_LOGIN: False})
    if not success:
            return AuthResponse(Response.INTERNAL_SERVER_ERROR)

    return AuthResponse(Response.OK)
