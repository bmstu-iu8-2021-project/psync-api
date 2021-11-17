from zipfile import ZipFile
import time
import os
from os.path import join
import shutil
from server_control.init import app

storage = app.config['UPLOAD_FOLDER']


def is_difference(server_path, content):
    content = {i['name'][i['name'].find(':') + 1:]: i['timestamp'] for i in content}
    archive = ZipFile(server_path, 'r')
    archive_content = {}
    for file in archive.namelist():
        archive_content['/' + file] = time.mktime(tuple(list(archive.getinfo(file).date_time) + [0, 0, 0]))
    archive.close()
    if set(content.keys()) - set(archive_content.keys()) == set() and set(archive_content.keys()) - set(
            content.keys()) == set():
        for file in content.keys():
            if abs(content[file] - archive_content[file]) > 5:
                return False
        return True
    return False


def get_dict(pair):
    folder = pair[1][pair[1].find(':') + 1:]
    archive = ZipFile(join(pair[0]), 'r')
    archive_content = {}
    for file in archive.namelist():
        archive_content[join('/', file).replace(folder, '')] = time.mktime(
            tuple(list(archive.getinfo(file).date_time) + [0, 0, 0]))
    return archive_content


# def compare_archives(current_archive, other_archive):
#     archive_one = get_dict(current_archive)
#     archive_two = get_dict(other_archive)
#     if set(archive_one.keys()) - set(archive_two.keys()) == set() and set(archive_two.keys()) - set(
#             archive_one.keys()) == set():
#         for file in archive_one.keys():
#             if abs(archive_one[file] - archive_two[file]) > 5:
#                 return False
#         return True
#     return False


def compare_archives(current_archive, other_archive):
    current_dict = get_dict(current_archive)
    other_dict = get_dict(other_archive)
    if set(current_dict.keys()) >= set(other_dict.keys()):
        for file in other_dict.keys():
            if current_dict[file] - other_dict[file] < -3:
                return False
        return True
    return False


def unzip_with_date(archive, destination):
    arch = ZipFile(archive, 'r')
    arch.extractall(destination)
    arch_data = {}
    arch_root = 'home'
    for file in arch.namelist():
        arch_root = file[:file.find('/')]
        arch_data[file] = time.mktime(tuple(list(arch.getinfo(file).date_time) + [0, 0, 0]))
    arch.close()
    for root, dirs, files in os.walk(join(destination, arch_root)):
        for file in files:
            os.utime(
                join(root, file),
                (arch_data[join(root, file).replace(destination + '/', '')],
                 arch_data[join(root, file).replace(destination + '/', '')])
            )


# во входе 0 - путь к архиву, 1 - путь к архивируемому, то есть выбранная папка внутри архива
# разархивируем архив
def merge(current_archive, other_archive):
    current = ZipFile(current_archive[0], 'r')
    temp = str(time.time())
    unzip_with_date(current_archive[0], join(storage, temp))
    current.close()

    other = ZipFile(other_archive[0], 'r')
    unzip_with_date(other_archive[0], storage[:-1])
    other.close()
    for file in os.listdir(join(storage, other_archive[1])):
        if os.path.isdir(join(storage, other_archive[1], file)):
            shutil.move(join(storage, other_archive[1], file),
                        join(storage, temp, current_archive[1]))
        else:
            shutil.copy2(join(storage, other_archive[1], file),
                         join(storage, temp, current_archive[1]))
    shutil.rmtree(join(storage, other_archive[1][:other_archive[1].find('/')]))

    merged = ZipFile(join(storage, f'{temp}.zip'), 'w')
    for root, dirs, files in os.walk(join(storage, temp)):
        for file in files:
            merged.write(join(root, file), join(root.replace(join(storage, temp), ''), file))
    merged.close()
    shutil.rmtree(join(storage, temp))
    os.rename(join(storage, f'{temp}.zip'), join(current_archive[0]))
