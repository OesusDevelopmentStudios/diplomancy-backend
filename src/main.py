from flask import request, Flask
from flask_cors import CORS

app = Flask("diplomancy-backend")
CORS(app)

@app.route("/api/v1/auth/logon", methods=["POST"])
def logon():
    print("Received logon request")
    print(request.get_json())
    return "Logon endpoint"

def execute():
    app.run(debug=True)
