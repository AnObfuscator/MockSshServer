from flask import Blueprint, request, jsonify
from mock_ssh_server import datastore

blueprint = Blueprint('api', __name__, url_prefix='/')


@blueprint.route('/commands', methods=['GET', 'POST', 'DELETE'])
def commands():
    if request.method == 'GET':
        return jsonify(datastore.get_commands()), 200

    if request.method == 'POST':
        datastore.add_command(request.json)
        return '', 201

    if request.method == 'DELETE':
        datastore.clear_commands()
        return '', 204


@blueprint.route('/users', methods=['GET', 'POST', 'DELETE'])
def users():
    if request.method == 'GET':
        return jsonify(datastore.get_users()), 200

    if request.method == 'POST':
        datastore.add_user(request.json)
        return '', 201

    if request.method == 'DELETE':
        datastore.clear_users()
        return '', 204


@blueprint.route('/keys', methods=['GET', 'POST', 'DELETE'])
def keys():
    if request.method == 'GET':
        return jsonify(datastore.get_keys()), 200

    if request.method == 'POST':
        datastore.add_key(request.json)
        return '', 201

    if request.method == 'DELETE':
        datastore.clear_users()
        return '', 204
