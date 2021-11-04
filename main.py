# Copyright 2021 Peter p.makretskii@gmail.com

from app_control.requests_processing import app, sio

if __name__ == '__main__':
    sio.run(app, host='0.0.0.0', port=8080, debug=True)

[]

# from flask import Flask
# from flask_socketio import SocketIO
#
# app = Flask(__name__)
# app.config['SECRET KEY'] = 'secret'
# socketio = SocketIO(app)
#
#
# @socketio.on('message')
# def handle_message(data):
#     print(f'received message: {data}')
#
#
# @socketio.event(namespace='/test')
# def handle_event(arg):
#     print(f'event: arg is {arg}')
#
#
# if __name__ == '__main__':
#     socketio.run(app, port=8080)


#
# from flask import Flask, request
# from flask_socketio import SocketIO, emit
#
# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'SecretKey@123'
# socket = SocketIO(app)
# users = set()
#
#
# @app.route('/auth/', methods=['GET'])
# def auth():
#     if request.method == 'GET':
#         users.add(request.args['login'])
#         # # socket.emit('online', {'login': request.args['login']})
#         # print(users)
#         return '1'
#     return '0'
#
#
# @app.route('/logout/', methods=['GET'])
# def logout():
#     if request.method == 'GET':
#         users.remove(request.args['login'])
#         # # socket.emit('offline', {'login': request.args['login']})
#         # print(users)
#         return '1'
#     return '0'
#
#
# @app.route('/sync/', methods=['GET'])
# def sync():
#     if request.method == 'GET':
#         login = request.args['login']
#         sync_to = request.args['sync_to']
#         return str(sync_to in users)
#     return '0'
#
#
# @socket.on('connect')
# def on_connect():
#     users.add(request.remote_addr)
#     print(users)
#
#
# @socket.on('disconnect')
# def on_disconnect():
#     users.remove(request.remote_addr)
#     print(users)
#
#
# # @socket.on('check')
# # def check(data):
# #     pass
# #
# #
# # @socket.on('online')
# # def online(data):
# #     emit('status_change', {'login': data['login'], 'status': 'online'}, broadcast=True)
# #
# #
# # @socket.on('offline')
# # def online(data):
# #     emit('status_change', {'login': data['login'], 'status': 'offline'}, broadcast=True)
#
#
# if __name__ == '__main__':
#     socket.run(app, host='0.0.0.0', port=8080, debug=True)

[]

# from flask import Flask, flash, Response, request
# from flask_socketio import SocketIO, emit
#
# app = Flask(__name__)
# app.config['SECRET_KEY'] = '?-.'
# # socketio = SocketIO(app)
#
#
# # @socketio.on('joined')
# # def handle_message(who):
# #     emit('back', who, broadcast=True)
#
# users = {}
#
#
# @app.route('/auth/', methods=['GET'])
# def auth():
#     if request.method == 'GET':
#         users[request.args['login']] = request.remote_addr
#         print(users)
#         return '1'
#     return '0'
#
#
# # @app.route('/sync/', methods=['GET'])
# # def sync():
# #     if request.method == 'GET':
# #         Response()
#
#
# @app.route('/logout/', methods=['GET'])
# def logout():
#     if request.method == 'GET':
#         users.pop(request.args['login'])
#         print(users)
#         return '1'
#     return '0'
#
#
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8080, debug=True)


# from flask import Flask, request
# from flask_socketio import SocketIO, emit, join_room, leave_room, send
#
# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'secret!'
# socketio = SocketIO(app)
# users = {}
#
#
# # @app.route('/auth/', methods=['GET'])
# # def auth():
# #     if request.method == 'GET':
# #         users[request.remote_addr] = request.args['login']
# #         room = request.args['room']
# #         join_room(room)
# #         send(f"{request.args['login']} has entered the room", to=room)
# #         print(users)
# #         return 'adios'
# #     return app.make_response(('Bad request', 400))
# #
# #
# # @app.route('/logout/', methods=['GET'])
# # def logout():
# #     if request.method == 'GET':
# #         users.pop(request.remote_addr)
# #         room = request.args['room']
# #         leave_room(room)
# #         send(f"{request.args['login']} has left the room", to=room)
# #         print(users)
# #         return 'bonjour'
# #     return app.make_response(('Bad request', 400))
# #
# #
# # @socketio.on('sync')
# # def sync(login):
# #     # print(request.args.keys())
# #     print(f'Sync {users[request.remote_addr]} >>>> {login}')
# #     emit(f'answer_{login}', {'data': 'Server'}, skip_sid='')
#
#
# @socketio.on('connect')
# def connect():
#     print(f'>>> Connected: {request.remote_addr}')
#
#
# @socketio.on('join')
# def on_join(data):
#     username = data['username']
#     room = data['room']
#     join_room(room)
#     send({'data': username + ' has entered the room'}, to=room)
#
#
# @socketio.on('leave')
# def on_leave(data):
#     username = data['username']
#     room = data['room']
#     leave_room(room)
#     send({'data': username + ' has left the room'}, to=room)
#
#
# @socketio.on('disconnect')
# def disconnect():
#     print(f'>>> Disconnected: {request.remote_addr}')
#
#
# if __name__ == '__main__':
#     socketio.run(app, host='0.0.0.0', port=8080, debug=True)
