from datetime import datetime

from database.sessions import SessionDb, Sessions


def _get_session_by_token_or_uuid(session_db: SessionDb, token: str|None = None, uuid: str|None = None):
    if token:
        return session_db.get_by_token(token)

    if uuid:
        return session_db.get_by_uuid(uuid)

    return None


def get_session_if_valid(session_db: SessionDb, token: str|None = None, uuid: str|None = None):
    data = _get_session_by_token_or_uuid(session_db, token, uuid)
    if not isinstance(data, dict):
        return None

    registered = data[Sessions.START]
    store_session = data[Sessions.STORE_SESSION]
    diff = datetime.now() - registered
    if store_session and diff.days > 30:
        session_db.remove(token)
        return None

    if not store_session and diff.days > 1:
        session_db.remove(token)
        return None

    return data
