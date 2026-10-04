import psycopg
import sys

from flask import Flask
from flask_cors import CORS

from database.core import DB, DBStatus
from endpoints.auth import auth_endpoint
from utils.log import log, Severity


def initilize():
    log("Startup", Severity.INF)

    try:
        assert len(sys.argv) == 4

        database = DB()
        database.initilize(sys.argv[1], sys.argv[2], sys.argv[3])

        # if database.status is not DBStatus.OK:
        #     log("Database failure. Reason: {0}".format(database.status.value), Severity.ERR)
        #     log("App will now terminate", Severity.ERR)
        #     return

        app = Flask("diplomancy-backend")
        CORS(app)

        app.register_blueprint(auth_endpoint)

        app.run(debug=True)

    except psycopg.OperationalError as error:
        log("Error: {0}".format(error), Severity.ERR)
        log("Unable to establish connection to database. App will now terminate", Severity.ERR)
        return
    except AssertionError:
        log("Expected to receive 4 arguments, but got {0}".format(len(sys.argv)), Severity.ERR)
        log("App will now terminate", Severity.ERR)
        return
    except:
        log("Unknown error has occured. App will now terminate.", Severity.ERR)
        return

    log("Shutting down...", Severity.INF)


if __name__ == '__main__':
    initilize()
