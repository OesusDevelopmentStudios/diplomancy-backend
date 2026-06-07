from enum import Enum


class Severity(Enum):
    DBG = "DBG"
    INF = "INF"
    WRN = "WRN"
    ERR = "ERR"


def log(message: any, severity: Severity = Severity.DBG):
    print("[DIPLOMNACY] " + severity.value + " " + str(message))
