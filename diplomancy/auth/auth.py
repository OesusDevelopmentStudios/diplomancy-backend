import os
import re
import hashlib
import hmac

from types import NoneType

from utils.http import Response
from utils.types import Database


class AuthResponse:
    def __init__(self, response: Response):
        self.response = response

    def code(self):
        return self.response.value


def handle_logon(db: Database, email: str|NoneType, username: str|NoneType, password: str|NoneType) -> AuthResponse:
    if email is None or username is None or password is None:
        return AuthResponse(Response.BAD_REQUEST)

    if not validate_password(password):
        return AuthResponse(Response.BAD_REQUEST)

    if is_email_taken(db, email):
        return AuthResponse(Response.CONFLICT)
    # TODO:
    # 1. Implement proper email generation
    # 2. Implement proper nickname generation -> Nickname#0000
    # 3. Start finally svaing data in the db
    salt, secret = hash_password(password)
    # TODO Finally store data in the db

    return AuthResponse(Response.CREATED)


def validate_password(password: str) -> bool:
    return re.match(r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$', password)


def hash_password(password: str) -> tuple[bytes, bytes]:
    salt = os.urandom(16)
    secret = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 1000000)
    return salt, secret


def verify_password(salt: bytes, secret: str, password: str) -> bool:
    return hmac.compare_digest(secret, hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 1000000))


def is_email_taken(db: Database, email: str) -> bool:
    return True
