from enum import Enum


class Response(Enum):
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    CONFLICT = 409
    INTERNAL_SERVER_ERROR = 500
