import psycopg
import sys

from flask import jsonify, request, Flask
from flask_cors import CORS

from utils.types import Database
from utils.log import log, Severity

from auth.auth import handle_logon

app = Flask("diplomancy-backend")
CORS(app)

db: Database


@app.route("/api/v1/auth/logon", methods=["POST"])
def logon():
    json = request.get_json()
    result = handle_logon(json.get('email', ''), json.get('username', ''), json.get('password'))

    response = jsonify()
    response.status_code = result.code()
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


def initilize():
    log("Startup", Severity.INF)

    try:
        assert len(sys.argv) == 4
        connection_str = "host=localhost port='{0}' dbname='{1}' user='diplomancy' password='{2}'" \
            .format(sys.argv[1], sys.argv[2], sys.argv[3])

        global db
        db = psycopg.connect(connection_str)
        app.run(debug=True)

    except psycopg.OperationalError:
        log("Unable to establish connection to database. App will now terminate", Severity.ERR)
    except AssertionError:
        log("Expected tp receive 4 arguments, but got {0}".format(len(sys.argv)), Severity.ERR)
    except:
        log("Unknown error has occured. App will now terminate.", Severity.ERR)

    log("Shutting down..", Severity.INF)


if __name__ == '__main__':
    initilize()
