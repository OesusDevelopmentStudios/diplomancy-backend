import os
import re
import hashlib
import hmac

from utils.database.users import UserTable, UserFields


def _get_data_by_username(user_db: UserTable, uuid: str):
    username, uid = uuid.split("#")
    if len(uid) != 4 or not uid.isdigit():
        return None

    return user_db.get_by_username_id(username, int(uid), [UserFields.EMAIL, UserFields.SALT, UserFields.SECRET])


def validate_password(password: str) -> bool:
    return re.match(r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$', password)


def hash_password(password: str) -> tuple[bytes, bytes]:
    salt = os.urandom(16)
    secret = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 1000000)
    return salt, secret


def verify_password(salt: bytes, secret: str, password: str) -> bool:
    return hmac.compare_digest(secret, hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 1000000))


def get_next_uid(user_db: UserTable, username: str) -> int:
    result = user_db.get_by_username(username, [UserFields.USERNAME_ID])
    if not result:
        return 0

    new_id = 0
    result.sort()
    for taken_id in result:
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
