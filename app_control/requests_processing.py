import datetime
import json
from functools import wraps

import jwt
from flask import request

from db_control import database_actions
from app_control.init import app


def token_required(req):
    @wraps(req)
    def decorated(*args, **kwargs):
        if 'Authorization' not in request.headers:
            return app.make_response(('Token was not find', 400))
        token = json.loads(request.headers['Authorization'])['token']
        if not token:
            return app.make_response(('Token was not find', 400))
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return app.make_response(('Token is wrong', 403))
        return req(*args, **kwargs)

    return decorated


@app.route('/auth/', methods=['GET'])
def auth():
    if request.method == 'GET':
        login = request.args['login']
        password = request.args['password']
        token = ''
        if database_actions.auth(login=login, password=password):
            token = jwt.encode({'user': login,
                                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
                                }, app.config['SECRET_KEY'])
            token = token.decode('UTF-8')
        return json.dumps({'token': token})


@app.route('/find_login/', methods=['GET'])
def find_login():
    if request.method == 'GET':
        return database_actions.find_login(login=request.args['login'])


@app.route('/find_email/', methods=['GET'])
def find_email():
    if request.method == 'GET':
        return database_actions.find_email(email=request.args['email'])


@app.route('/get_email/', methods=['GET'])
@token_required
def get_email():
    if request.method == 'GET':
        return database_actions.get_email(login=request.args['login'])


@app.route('/get_password/', methods=['GET'])
@token_required
def get_password():
    if request.method == 'GET':
        return database_actions.get_password(login=request.args['login'])


@app.route('/add_user/', methods=['GET'])
def add_user():
    if request.method == 'GET':
        database_actions.add_user(
            login=request.args['login'],
            email=request.args['email'],
            password=request.args['password']
        )
        return str(True)


@app.route('/delete_user/', methods=['GET'])
@token_required
def delete_user():
    if request.method == 'GET':
        database_actions.delete_user(login=request.args['login'])
        return str(True)


@app.route('/change_mail/', methods=['GET'])
@token_required
def change_mail():
    if request.method == 'GET':
        database_actions.change(login=request.args['login'], field='mail', new_value=request.args['email'])
        return str(True)


@app.route('/change_password/', methods=['GET'])
@token_required
def change_password():
    if request.method == 'GET':
        database_actions.change(login=request.args['login'], field='password', new_value=request.args['password'])
        return str(True)


@app.route('/add_version/', methods=['GET'])
@token_required
def add_version():
    if request.method == 'GET':
        files = json.loads(request.data.decode('UTF-8'))
        login = files['login']
        mac = files['mac']
        path_file = files['path_file']
        ver = files['new_version']
        database_actions.add_folder(
            login=login,
            mac=mac,
            folder_path=path_file,
            version=ver
        )
        for file in files['files']:
            database_actions.add_files(
                login=login,
                mac=mac,
                folder_path=path_file,
                file_path=file,
                edited_at=float(files['files'][file]),
                version=ver
            )
        return str(True)


# add folder
@app.route('/update_version/', methods=['GET'])
@token_required
def update_version():
    if request.method == 'GET':
        files = json.loads(request.data.decode('UTF-8'))
        login = files['login']
        mac = files['mac']
        path_file = files['path_file']
        o_ver = files['old_version']
        n_ver = files['new_version']
        database_actions.delete_folder(
            login=login,
            mac=mac,
            folder_path=path_file,
            version=o_ver
        )
        database_actions.add_folder(
            login=login,
            mac=mac,
            folder_path=path_file,
            version=n_ver
        )
        for file in files['files']:
            database_actions.add_files(
                login=login,
                mac=mac,
                folder_path=path_file,
                file_path=file,
                edited_at=float(files['files'][file]),
                version=n_ver
            )
        return str(True)


# delete folder
@app.route('/delete_version/', methods=['GET'])
@token_required
def delete_version():
    if request.method == 'GET':
        database_actions.delete_folder(
            login=request.args['login'],
            mac=request.args['mac'],
            folder_path=request.args['folder_path'],
            version=request.args['version']
        )
        return str(True)


@app.route('/find_version/', methods=['GET'])
@token_required
def find_version():
    if request.method == 'GET':
        return str(int(database_actions.find_version(
            login=request.args['login'],
            mac=request.args['mac'],
            folder_path=request.args['folder_path'],
            version=request.args['version']
        )))
