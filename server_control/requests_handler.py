import datetime
import json
import os
from functools import wraps

import flask
from flask import request
from flask_socketio import join_room, leave_room
import jwt

from db_control import database_actions
from server_control.init import app, sio


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
        mac = request.args['mac']
        token = ''
        if database_actions.auth(
                login=login,
                password=password,
                mac=mac,
        ):
            token = jwt.encode({'user': login,
                                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
                                }, app.config['SECRET_KEY'])
            token = token.decode('UTF-8')
        return json.dumps({'token': token})
    return app.make_response(('Bad request', 400))


@app.route('/find_login/', methods=['GET'])
def find_login():
    if request.method == 'GET':
        return database_actions.find_login(login=request.args['login'])
    return app.make_response(('Bad request', 400))


@app.route('/find_email/', methods=['GET'])
def find_email():
    if request.method == 'GET':
        return database_actions.find_email(email=request.args['email'])
    return app.make_response(('Bad request', 400))


@app.route('/get_email/', methods=['GET'])
@token_required
def get_email():
    if request.method == 'GET':
        return database_actions.get_email(login=request.args['login'])
    return app.make_response(('Bad request', 400))


@app.route('/get_password/', methods=['GET'])
@token_required
def get_password():
    if request.method == 'GET':
        return database_actions.get_password(login=request.args['login'])
    return app.make_response(('Bad request', 400))


@app.route('/add_user/', methods=['GET'])
def add_user():
    if request.method == 'GET':
        database_actions.add_user(
            login=request.args['login'],
            mac=request.args['mac'],
            email=request.args['email'],
            password=request.args['password'],
        )
        return str(True)
    return app.make_response(('Bad request', 400))


@app.route('/delete_user/', methods=['GET'])
@token_required
def delete_user():
    if request.method == 'GET':
        database_actions.delete_user(login=request.args['login'])
        return str(True)
    return app.make_response(('Bad request', 400))


@app.route('/change_mail/', methods=['GET'])
@token_required
def change_mail():
    if request.method == 'GET':
        database_actions.change(
            login=request.args['login'],
            field='email',
            new_value=request.args['email'],
        )
        return str(True)
    return app.make_response(('Bad request', 400))


@app.route('/change_password/', methods=['GET'])
@token_required
def change_password():
    if request.method == 'GET':
        database_actions.change(
            login=request.args['login'],
            field='password',
            new_value=request.args['password'],
        )
        return str(True)
    return app.make_response(('Bad request', 400))


# add folder
@app.route('/add_version/', methods=['GET'])
@token_required
def add_version():
    if request.method == 'GET':
        files = json.loads(request.data.decode('UTF-8'))
        database_actions.add_folder(
            login=files['login'],
            mac=files['mac'],
            folder_path=files['path_file'],
            version=files['new_version'],
            is_actual=files['is_actual'],
            path=os.path.join(app.config['UPLOAD_FOLDER'], '_'.join(
                [files['login'], files['path_file'][files['path_file'].rfind('/') + 1:],
                 files['new_version']]) + '.zip')
        )
        return str(True)
    return app.make_response(('Bad request', 400))


@app.route('/upload_folder/', methods=['GET'])
@token_required
def upload_folder():
    if request.method == 'GET':
        file_get = request.files['file']
        if file_get:
            filename = file_get.filename
            file_get.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return str(True)
    return app.make_response(('Bad request', 400))


@app.route('/delete_version/', methods=['GET'])
@token_required
def delete_version():
    if request.method == 'GET':
        path = database_actions.delete_version(
            login=request.args['login'],
            mac=request.args['mac'],
            folder_path=request.args['folder_path'],
            version=request.args['version'],
        )
        os.remove(path)
        return str(True)
    return app.make_response(('Bad request', 400))


@app.route('/find_version/', methods=['GET'])
@token_required
def find_version():
    if request.method == 'GET':
        return (database_actions.find_version(
            login=request.args['login'],
            mac=request.args['mac'],
            folder_path=request.args['folder_path'],
            version=request.args['version'],
        ))
    return app.make_response(('Bad request', 400))


@app.route('/get_folders/', methods=['GET'])
@token_required
def get_folders():
    if request.method == 'GET':
        return database_actions.get_folders(
            login=request.args['login'],
            mac=request.args['mac'],
        )
    return app.make_response(('Bad request', 400))


@app.route('/make_actual/', methods=['GET'])
@token_required
def make_actual():
    if request.method == 'GET':
        database_actions.make_actual(
            login=request.args['login'],
            mac=request.args['mac'],
            path=request.args['path'],
            version=request.args['version'],
        )
        return str(True)
    return app.make_response(('Bad request', 400))


@app.route('/check_actuality/', methods=['GET'])
@token_required
def check_actuality():
    if request.method == 'GET':
        return database_actions.get_difference(data=request.json)
    return app.make_response(('Bad request', 400))


@app.route('/make_no_actual/', methods=['GET'])
@token_required
def make_no_actual():
    if request.method == 'GET':
        database_actions.make_no_actual(
            login=request.args['login'],
            mac=request.args['mac'],
            path=request.args['path'],
        )
        return str(True)
    return app.make_response(('Bad request', 400))


@app.route('/get_actual_version/', methods=['GET'])
@token_required
def get_actual_version():
    if request.method == 'GET':
        return database_actions.get_actual_version(
            login=request.args['login'],
            mac=request.args['mac'],
            path=request.args['path'],
        )
    return app.make_response(('Bad request', 400))


@app.route('/download_folder/', methods=['GET'])
@token_required
def download_folder():
    if request.method == 'GET':
        response = flask.make_response()
        if not request.args['flag']:
            response.data = database_actions.download_folder(
                login=request.args['login'],
                mac=request.args['mac'],
                path=request.args['path'],
                version=request.args['version'],
            )
        else:
            response.data = database_actions.download_folder(
                login=request.args['login'],
                mac=request.args['mac'],
                path=request.args['path'],
            )
        return response
    return app.make_response(('Bad request', 400))


@app.route('/synchronize/', methods=['GET'])
@token_required
def synchronize():
    if request.method == 'GET':
        other_user = request.args['other_user']
        if other_user not in users:
            return str(False)
        sio.send({'type': 'request_to_synchronize',
                  'current_user': request.args['current_user'],
                  'current_folder': request.args['current_folder'],
                  'current_mac': request.args['current_mac'],
                  'other_user': request.args['other_user']}, to=request.args['room'])
        return str(True)
    return app.make_response(('Bad request', 400))


users = []


@sio.on('join_room')
def on_join(data):
    users.append(data['current_user'])
    room = data['room']
    join_room(room)
    print('joined')


@sio.on('leave_room')
def on_leave(data):
    users.remove(data['current_user'])
    room = data['room']
    leave_room(room)
    print('left')


@sio.on('send_answer')
def on_answer(data):
    choice = data['choice']
    data['type'] = 'answer'
    sio.send(data, to=data['room'])
    if choice:
        database_actions.synchronize(
            current=(data['current_user'], data['current_mac'], data['current_folder']),
            other=(data['other_user'], data['other_mac'], data['other_folder'])
        )


@app.route('/get_synchronized/', methods=['GET'])
@token_required
def get_synchronized():
    if request.method == 'GET':
        return database_actions.get_synchronized(
            login=request.args['login'],
            mac=request.args['mac']
        )
    return app.make_response(('Bad request', 400))


@app.route('/terminate_sync/', methods=['GET'])
@token_required
def terminate_sync():
    if request.method == 'GET':
        database_actions.terminate_sync(
            current_login=request.args['current_login'],
            other_login=request.args['other_login'],
            current_folder=request.args['current_folder'],
            other_folder=request.args['other_folder'],
            current_mac=request.args['current_mac']
        )
        return str(True)
    return app.make_response(('Bad request', 400))


@app.route('/check_synchronized/', methods=['GET'])
@token_required
def check_synchronized():
    if request.method == 'GET':
        return database_actions.check_synchronized(
            login=request.args['login'],
            mac=request.args['mac']
        )
    return app.make_response(('Bad request', 400))


@app.route('/update_version/', methods=['GET'])
@token_required
def update_version():
    if request.method == 'GET':
        database_actions.update_version(
            login=request.args['login'],
            mac=request.args['mac'],
            path_file=request.args['path_file'],
            version=request.args['version']
        )
        return str(True)
    return app.make_response(('Bad request', 400))


# @app.route('/terminate_all_sync/', methods=['GET'])
# @token_required
# def terminate_all_sync():
#     if request.method == 'GET':
#         database_actions.terminate_all_sync(
#             login=request.args['login'],
#             mac=request.args['mac'],
#             path=request.args['path']
#         )
#         return str(True)
#     return app.make_response(('Bad request', 400))


# @app.route('/terminate_pair_sync/', methods=['GET'])
# @token_required
# def terminate_pair_sync():
#     if request.method == 'GET':
#         database_actions.terminate_pair_sync(
#             current_login=request.args['current_login'],
#             current_mac=request.args['current_mac'],
#             current_folder=request.args['current_folder'],
#
#         )
#     return app.make_response(('Bad request', 400))


@app.route('/synchronize_folder/', methods=['GET'])
@token_required
def synchronize_folder():
    if request.method == 'GET':
        database_actions.synchronize_folder(
            current_login=request.args['current_login'],
            current_mac=request.args['current_mac'],
            other_login=request.args['current_login'],
            current_folder=request.args['current_login'],
            other_folder=request.args['current_login']
        )
        return str(True)
    return app.make_response(('Bad request', 400))
