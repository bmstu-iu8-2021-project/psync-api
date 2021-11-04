# Copyright 2021 Peter p.makretskii@gmail.com

from app_control.requests_processing import app, sio

if __name__ == '__main__':
    sio.run(app, host='0.0.0.0', port=8080, debug=True)
