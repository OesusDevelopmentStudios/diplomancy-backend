import os
import re
import hashlib
import hmac

from uuid import uuid4

from utils.database.users import UserTable, UserFields
from utils.database.helpers import is_token_valid


def _get_data_by_username(user_db: UserTable, uuid: str):
    username, uid = uuid.split("#")
    if len(uid) != 4 or not uid.isdigit():
        return None

    return user_db.get_by_username_id(username, int(uid), [UserFields.EMAIL, UserFields.SALT, UserFields.SECRET])


def _get_sorted_ids(user_db: UserTable, username: str):
    result = user_db.get_by_username(username, [UserFields.USERNAME_ID])
    if not result:
        return []

    if isinstance(result, dict):
        return [result[UserFields.USERNAME_ID]]

    return sorted([id[UserFields.USERNAME_ID] for id in result])


def validate_password(password: str) -> bool:
    return re.match(r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$', password)


def hash_password(password: str) -> tuple[bytes, bytes]:
    salt = os.urandom(16)
    secret = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 1000000)
    return salt, secret


def verify_password(salt: bytes, secret: str, password: str) -> bool:
    return hmac.compare_digest(secret, hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 1000000))


def get_next_uid(user_db: UserTable, username: str) -> int:
    new_id = 0
    ids = _get_sorted_ids(user_db, username)
    for taken_id in ids:
        if taken_id > new_id:
            return new_id
        if new_id == taken_id:
            new_id = new_id + 1

    return new_id


def get_uuid(username: str, uid: int) -> str:
    zeros = 4 - len(str(uid))
    return username + "#" + zeros * "0" + str(uid)


def get_user_data(user_db: UserTable, user_id: str):
    if "#" in user_id:
        return _get_data_by_username(user_db, user_id)
    else:
        return user_db.get_by_email(user_id, [UserFields.EMAIL, UserFields.SALT, UserFields.SECRET])


def get_unique_token(user_db) -> str:
    while True:
        token = uuid4()
        if not is_token_valid(user_db, str(token)):
            return str(token)
