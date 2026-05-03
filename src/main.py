from flask import request, Flask

app = Flask("diplomancy-backend")

@app.route("/api/v1/auth/logon/<uname>", methods=["POST"])
def logon(uname):
    print(uname)
    print(request.get_json())
    return "Logon endpoint"

def execute():
    app.run(debug=True)
