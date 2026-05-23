from flask import jsonify, request, Flask
from flask_cors import CORS

app = Flask("diplomancy-backend")
CORS(app)

@app.route("/api/v1/auth/logon", methods=["POST"])
def logon():
    print("Received logon request")
    print(request.get_json())

    response = jsonify({'some': 'data'})
    # response.status_code = 404
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


def execute():
    app.run(debug=True)
