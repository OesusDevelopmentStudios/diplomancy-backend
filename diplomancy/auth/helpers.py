import os
import re
import hashlib
import hmac

from utils.database.users import UserTable, UserFields


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
