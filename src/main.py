from flask import Flask

app = Flask("diplomancy-backend")

@app.route("/logon", methods=["POST"])
def logon():
    return "Logon endpoint"

def execute():
    app.run(debug=True)
