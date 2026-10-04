from flask import Blueprint, jsonify, request
from database.core import DB

from utils.log import log, Severity

from endpoints.helpers.auth import handle_logon, handle_login, handle_validate, handle_logout


database = DB()
auth_endpoint = Blueprint('auth', __name__, url_prefix='/api/v1/auth')


@auth_endpoint.route("/logon", methods=["POST"])
def logon():
    json = request.get_json()

    # TODO: LOG only for development purposes, remove in production
    log("Received logon request: {0}".format(json), Severity.DBG)

    result = handle_logon(database.users, json.get('email', ''), json.get('username', ''), json.get('password', ''))
    response = jsonify(result.dict())
    response.status_code = result.code()
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@auth_endpoint.route("/login", methods=["POST"])
def login():
    json = request.get_json()

    # TODO: LOG only for development purposes, remove in production
    log("Received login request: {0}".format(json), Severity.DBG)

    result = handle_login(
        database.users, database.sessions, json.get('id', ''), json.get('password', ''), json.get('remember', False))
    response = jsonify(result.dict())
    response.status_code = result.code()
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@auth_endpoint.route('/validate', methods=["POST"])
def validate():
    json = request.get_json()

    # TODO: LOG only for development purposes, remove in production
    log("Received validate request: {0}".format(json), Severity.DBG)

    result = handle_validate(database.users, database.sessions, json.get('token', None))
    response = jsonify(result.dict())
    response.status_code = result.code()
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@auth_endpoint.route("/logout", methods=["POST"])
def logout():
    json = request.get_json()

    # TODO: LOG only for development purposes, remove in production
    log("Received logout request: {0}".format(json), Severity.DBG)

    result = handle_logout(database.sessions, json.get('token', None))
    response = jsonify(result.dict())
    response.status_code = result.code()
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response
