from enum import Enum


class Response(Enum):
    CREATED = 201
    BAD_REQUEST = 400
    CONFLICT = 409
