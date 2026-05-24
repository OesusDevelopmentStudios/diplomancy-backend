import psycopg

from flask import jsonify, request, Flask
from flask_cors import CORS


from diplomancy.utils.types import Database


app = Flask("diplomancy-backend")
CORS(app)

db: Database


@app.route("/api/v1/auth/logon", methods=["POST"])
def logon():
    print("Received logon request")
    print(request.get_json())

    response = jsonify({'some': 'data'})
    # response.status_code = 404
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


def execute():
    try:
        global db
        db = psycopg.connect("dbname=diplomancy user=backend")
        app.run(debug=True)
    except psycopg.OperationalError:
        print("Unable to establish connection to database. App will now terminate")
    except:
        print("Unknown error has occured. App will now terminate.")
