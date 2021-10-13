# Copyright 2021 Peter p.makretskii@gmail.com

from app_control.requests_processing import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
