import psycopg

from flask import jsonify, request, Flask
from flask_cors import CORS


from utils.types import Database
from utils.log import log, Severity


app = Flask("diplomancy-backend")
CORS(app)

db: Database


@app.route("/api/v1/auth/logon", methods=["POST"])
def logon():
    log("Received logon request")
    log(request.get_json())

    response = jsonify({'some': 'data'})
    # response.status_code = 404
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


def initilize():
    log("Startup", Severity.INF)
    # Command to compose the container: podman compose --file database/compose.yaml up -d
    # TODO: Move path, db name and password to env variable so that both python and db script can read it
    try:
        global db
        db = psycopg.connect("host=localhost dbname=diplomancy_db user='diplomancy' password='password1234'")
        app.run(debug=True)
    except psycopg.OperationalError:
        print("Unable to establish connection to database. App will now terminate")
    except:
        print("Unknown error has occured. App will now terminate.")

    log("Shutting down..", Severity.INF)


if __name__ == '__main__':
    initilize()
