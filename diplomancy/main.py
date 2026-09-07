import psycopg
import sys

from flask import jsonify, request, Flask
from flask_cors import CORS

from utils.log import log, Severity
from utils.database.users import UserTable

from auth.auth import handle_logon, handle_login


app = Flask("diplomancy-backend")
CORS(app)

user_db: UserTable


API_V1 = "/api/v1/"


@app.route(API_V1 + "auth/logon", methods=["POST"])
def auth_logon():
    json = request.get_json()

    # TODO: LOG only for development purposes, remove in production
    log("Received logon request: {0}".format(json), Severity.DBG)

    result = handle_logon(user_db, json.get('email', ''), json.get('username', ''), json.get('password', ''))
    response = jsonify(result.dict())
    response.status_code = result.code()
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@app.route(API_V1 + "auth/login", methods=["POST"])
def auth_login():
    json = request.get_json()

    # TODO: LOG only for development purposes, remove in production
    log("Received login request: {0}".format(json), Severity.DBG)

    result = handle_login(user_db, json.get('id', ''), json.get('password', ''), json.get('remember', None))
    response = jsonify(result.dict())
    response.status_code = result.code()
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@app.route(API_V1 + "auth/validate", methods=["POST"])
def auth_validate():
    json = request.get_json()

    # TODO: LOG only for development purposes, remove in production
    log("Received validate request: {0}".format(json), Severity.DBG)

    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


def initilize():
    log("Startup", Severity.INF)

    try:
        assert len(sys.argv) == 4
        connection_str = "host=localhost port='{0}' dbname='{1}' user='diplomancy' password='{2}'" \
            .format(sys.argv[1], sys.argv[2], sys.argv[3])

        global user_db
        db = psycopg.connect(connection_str)
        user_db = UserTable(db)

        if not user_db.is_initilized():
            log("Failed to initilize database", Severity.ERR)
        else:
            app.run(debug=True)

    except psycopg.OperationalError as error:
        log("Unable to establish connection to database. App will now terminate", Severity.ERR)
        log("Error: {0}".format(error), Severity.ERR)
    except AssertionError:
        log("Expected to receive 4 arguments, but got {0}".format(len(sys.argv)), Severity.ERR)
    except:
        log("Unknown error has occured. App will now terminate.", Severity.ERR)

    log("Shutting down..", Severity.INF)


if __name__ == '__main__':
    initilize()
