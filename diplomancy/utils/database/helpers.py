from datetime import datetime

from utils.database.users import UserTable, UserFields


def is_token_valid(user_db: UserTable, token: str):
    data = user_db.get_by_token(token, [UserFields.VALID_SINCE, UserFields.SAVE_LOGIN])
    if not isinstance(data, dict):
        return False

    valid_since = data[UserFields.VALID_SINCE]
    save_login = data[UserFields.SAVE_LOGIN]
    diff = datetime.now() - valid_since
    if save_login and diff.days > 30:
        return False

    if not save_login and diff.days > 1:
        return False

    return True
