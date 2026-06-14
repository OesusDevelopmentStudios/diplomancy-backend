import os
import re
import hashlib
import hmac

from types import NoneType

from utils.http import Response
from utils.log import log, Severity


class AuthResponse:
    def __init__(self, response: Response):
        self.response = response

    def code(self):
        return self.response.value


def handle_logon(email: str|NoneType, username: str|NoneType, password: str|NoneType) -> AuthResponse:
    if email is None or username is None or password is None:
        log("Bad request! Email: " + ("None" if email is None else "Ok")
            + ", Username: " + ("None" if username is None else "Ok")
            + ", Password: " + ("None" if password is None else "Ok"), Severity.WRN)
        return AuthResponse(Response.BAD_REQUEST)

    if not validate_password(password):
        log("Invalid password! Password: " + password, Severity.WRN)
        return AuthResponse(Response.BAD_REQUEST)

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
