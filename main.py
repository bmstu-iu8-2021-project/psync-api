# Copyright 2021 Peter p.makretskii@gmail.com

from server_control.requests_handler import app, sio

if __name__ == '__main__':
    sio.run(app, host='0.0.0.0', port=12355)
