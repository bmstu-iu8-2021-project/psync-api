# Copyright 2021 Peter p.makretskii@gmail.com

from app_control.requests_processing import app
import db_control.database_actions

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
    # print(db_control.database_actions.find_version(
    #     login='peter',
    #     mac='mac',
    #     folder_path='/home',
    #     version='v1.1'
    # ))
