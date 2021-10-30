import os
import zipfile
from app_control.init import app
import time


def get_difference(local_archive):
    to_update = {'folder_name': set()}
    for i in range(len(local_archive['zip_name'])):
        archive = zipfile.ZipFile(os.path.join(app.config['UPLOAD_FOLDER'], local_archive['zip_name'][i]), 'r')
        server_archive = {}
        for file in archive.namelist():
            server_archive['/' + file] = time.mktime(tuple(list(archive.getinfo(file).date_time) + [0, 0, 0]))

        if set(server_archive.keys()) != set(local_archive['content'][i]):
            to_update['folder_name'].add(local_archive['folder_name'][i])
        else:
            for file in server_archive:
                if abs(server_archive[file] - local_archive['content'][i][file]) > 10:
                    to_update['folder_name'].add(local_archive['folder_name'][i])

    to_update['folder_name'] = list(to_update['folder_name'])
    return to_update
