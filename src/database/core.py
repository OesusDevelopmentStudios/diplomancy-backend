import psycopg

from enum import Enum

from utils.singleton import singleton

from database.users import UserDb


class DBStatus(Enum):
    OK = "Ok"
    NOT_INITILIZED = "Not initilized"


@singleton
class DB:
    def __init__(self):
        self.status = DBStatus.NOT_INITILIZED

    def initilize(self, port:str, name: str, password: str):
        connection_str = \
            "host=localhost port='{0}' dbname='{1}' user='diplomancy' password='{2}'".format(port, name, password)
        self._db = psycopg.connect(connection_str)
        self.user = UserDb(self._db)
