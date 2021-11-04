import codecs
import json
import os
import bcrypt
import datetime

from db_control.init import connect, close


def auth(login, password, mac):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT password, id FROM coursework.public.persons WHERE login = '{login}';")
        pack = cursor.fetchone()
        if pack is None:
            close(conn)
            return False
        pw, person_id = pack
        if pw:
            if bcrypt.checkpw(password.encode('UTF-8'), pw.encode('UTF-8')):
                cursor.execute(f"SELECT id FROM coursework.public.hosts WHERE mac = '{mac}'")
                host_id = cursor.fetchone()
                if host_id is None:
                    host_id = add_host(mac)
                    cursor.execute(f"INSERT INTO coursework.public.agent (person_id, host_id) "
                                   f"VALUES({person_id}, {host_id});")
                close(conn)
                return True
    close(conn)
    return False


def add_host(mac):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f"INSERT INTO coursework.public.hosts (mac) VALUES('{mac}')")
        cursor.execute(f"SELECT id FROM coursework.public.hosts WHERE mac = '{mac}'")
        host_id = cursor.fetchone()
    close(conn)
    return host_id


def find_login(login):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT email FROM coursework.public.persons WHERE login = '{login}';")
        email = cursor.fetchone()
    close(conn)
    return str(email is None)


def find_email(email):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT login FROM coursework.public.persons WHERE email = '{email}';")
        login = cursor.fetchone()
    close(conn)
    return str(login is None)


def get_email(login):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT email FROM coursework.public.persons WHERE login = '{login}';")
        email = cursor.fetchone()
    close(conn)
    return email[0]


def get_password(login):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT password FROM coursework.public.persons WHERE login = '{login}';")
        password = cursor.fetchone()
    close(conn)
    return password[0]


def add_user(login, mac, email, password):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            INSERT INTO coursework.public.persons (login, email, password) VALUES('{login}', '{email}', '{password}');
        ''')
        cursor.execute(f"INSERT INTO coursework.public.hosts (mac) VALUES('{mac}') ON CONFLICT DO NOTHING;")
        cursor.execute(f"SELECT id FROM coursework.public.persons WHERE login = '{login}'")
        person_id = int(cursor.fetchone()[0])
        cursor.execute(f"SELECT id FROM coursework.public.hosts WHERE mac = '{mac}'")
        host_id = int(cursor.fetchone()[0])
        cursor.execute(f"INSERT INTO coursework.public.agent (person_id, host_id) VALUES({person_id}, {host_id});")
    close(conn)


def delete_user(login):
    person_id = get_person_id(login)
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT id FROM coursework.public.agent WHERE person_id = {person_id};")
        agent_ids = [i[0] for i in cursor.fetchall()]
        for agent_id in agent_ids:
            cursor.execute(f"SELECT id FROM coursework.public.resources WHERE agent_id = {agent_id};")
            res_ids = [i[0] for i in cursor.fetchall()]
            for res_id in res_ids:
                cursor.execute(f"SELECT path FROM coursework.public.versions WHERE resources_id = {res_id}")
                [os.remove(i[0]) for i in cursor.fetchall()]
        cursor.execute(f"DELETE FROM coursework.public.persons WHERE login = '{login}';")
    close(conn)


def change(login, field, new_value):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f"UPDATE coursework.public.persons SET {field} = '{new_value}' WHERE login = '{login}'")
    close(conn)


# # add version
# def add_folder(login, mac, folder_path, version):
#     conn = connect()
#     with conn.cursor() as cursor:
#         cursor.execute(f'''
#             SELECT user_id FROM coursework.public.folders WHERE
#                 login = '{login}' AND
#                 mac = '{mac}';
#         ''')
#         user_id = cursor.fetchone()
#         if user_id is None:
#             cursor.execute(f"SELECT MAX(user_id) FROM coursework.public.folders")
#             user_id = cursor.fetchone()
#             if user_id[0] is None:
#                 user_id = 0
#             else:
#                 user_id = user_id[0] + 1
#         else:
#             user_id = user_id[0]
#
#         cursor.execute(f'''
#             SELECT folder_id FROM coursework.public.folders WHERE
#                 login = '{login}' AND
#                 mac = '{mac}' AND
#                 folder = '{folder_path}' AND
#                 version = '{version}';
#         ''')
#         folder_id = cursor.fetchone()
#         if folder_id is None:
#             cursor.execute(f"SELECT MAX(folder_id) FROM coursework.public.folders")
#             folder_id = cursor.fetchone()
#             if folder_id[0] is None:
#                 folder_id = 0
#             else:
#                 folder_id = folder_id[0] + 1
#         else:
#             folder_id = folder_id[0]
#
#         cursor.execute(f'''
#             INSERT INTO coursework.public.folders VALUES(
#                 '{login}',
#                 '{mac}',
#                 {user_id},
#                 '{folder_path}',
#                 '{version}',
#                 {folder_id}
#         );''')
#     close(conn)


def get_person_id(login):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT id FROM coursework.public.persons WHERE login = '{login}'")
        person_id = cursor.fetchone()[0]
    close(conn)
    return person_id


def get_host_id(mac):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT id FROM coursework.public.hosts WHERE mac = '{mac}'")
        host_id = cursor.fetchone()[0]
    close(conn)
    return host_id


def get_agent_id(login, mac):
    person_id = get_person_id(login)
    host_id = get_host_id(mac)
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT id FROM coursework.public.agent WHERE person_id = {person_id} AND host_id = {host_id}")
        agent_id = cursor.fetchone()[0]
    close(conn)
    return agent_id


# add version
def add_folder(login, mac, folder_path, version, is_actual, path):
    agent_id = get_agent_id(login, mac)
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            SELECT id FROM coursework.public.resources WHERE agent_id = {agent_id} AND path = '{folder_path}'
        ''')
        if cursor.fetchone() is None:
            cursor.execute(f'''
                INSERT INTO coursework.public.resources (agent_id, path) VALUES({agent_id}, '{folder_path}');
            ''')
        cursor.execute(
            f"SELECT id FROM coursework.public.resources WHERE agent_id = {agent_id} AND path = '{folder_path}'"
        )
        res_id = int(cursor.fetchone()[0])

        cursor.execute(f'''
            INSERT INTO coursework.public.versions (resources_id, version, created_at, is_actual, path) 
            VALUES({res_id}, '{version}', '{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}', 
            {is_actual}, '{path}');
        ''')
    close(conn)


# delete version
def delete_version(login, mac, folder_path, version):
    agent_id = get_agent_id(login, mac)
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            SELECT id FROM coursework.public.resources WHERE agent_id = {agent_id} AND path = '{folder_path}';
        ''')
        resources_id = cursor.fetchone()[0]
        cursor.execute(f'''
            SELECT path FROM coursework.public.versions WHERE resources_id = {resources_id} AND version = '{version}';
        ''')
        path = cursor.fetchone()[0]
        cursor.execute(f'''
            DELETE FROM coursework.public.versions WHERE resources_id = {resources_id} AND version = '{version}';
        ''')
        cursor.execute(f"SELECT id FROM coursework.public.versions WHERE resources_id = {resources_id};")
        if cursor.fetchone() is None:
            cursor.execute(f"DELETE FROM coursework.public.resources WHERE agent_id = {agent_id} AND "
                           f"path = '{folder_path}';")
    close(conn)
    return path


def find_version(login, mac, folder_path, version):
    agent_id = get_agent_id(login, mac)
    get = None
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(
            f"SELECT id FROM coursework.public.resources WHERE agent_id = {agent_id} AND path = '{folder_path}'"
        )
        resources_id = cursor.fetchone()
        if not (resources_id is None):
            cursor.execute(
                f"SELECT version FROM coursework.public.versions "
                f"WHERE resources_id = {resources_id[0]} AND version = '{version}'"
            )
            get = cursor.fetchone()
    close(conn)
    return str(get is None)


# def get_json(output, data_, *args):
#     if output is None:
#         output = dict()
#     for arg in args:
#         output[arg] = list()
#     for row in data_:
#         for arg in args:
#             output[arg].append(row[args.index(arg)])
#     return output


def get_json(output, path, version_info, *args):
    if output is None or len(output.keys()) == 0:
        output = dict()
        for arg in args:
            output[arg] = list()
    for row in version_info:
        output[args[0]].append(path)
        for arg in args[1:]:
            output[arg].append(str(row[args[1:].index(arg)]))
    return output


def get_folders(login, mac):
    agent_id = get_agent_id(login, mac)
    folders = {}
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT id, path FROM coursework.public.resources WHERE agent_id = {agent_id}")
        resources_info = cursor.fetchall()
        for pair in resources_info:
            cursor.execute(f'''
                SELECT version, created_at, is_actual FROM coursework.public.versions WHERE resources_id = {pair[0]}
            ''')
            version_info = cursor.fetchall()
            folders = get_json(folders, pair[1], version_info, 'folder', 'version', 'created_at', 'is_actual')
    close(conn)
    return json.dumps(folders)


def make_actual(login, mac, path, version):
    agent_id = get_agent_id(login, mac)
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(
            f"SELECT id FROM coursework.public.resources WHERE agent_id = {agent_id} AND path = '{path}'"
        )
        resources_id = cursor.fetchone()[0]
        cursor.execute(f"UPDATE coursework.public.versions SET is_actual = False WHERE resources_id = {resources_id}")
        cursor.execute(f"UPDATE coursework.public.versions SET is_actual = True "
                       f"WHERE resources_id = {resources_id} AND version = '{version}'")
    close(conn)


def make_no_actual(login, mac, path):
    agent_id = get_agent_id(login, mac)
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(
            f"SELECT id FROM coursework.public.resources WHERE agent_id = {agent_id} AND path = '{path}'"
        )
        resources_id = cursor.fetchone()[0]
        cursor.execute(f"UPDATE coursework.public.versions SET is_actual = False WHERE resources_id = {resources_id}")
    close(conn)


def get_resources_id(agent_id, path):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT id FROM coursework.public.resources WHERE agent_id = {agent_id} AND path = '{path}'")
        resources_id = cursor.fetchone()[0]
    close(conn)
    return resources_id


def get_actual_version(login, mac, path):
    agent_id = get_agent_id(login, mac)
    resources_id = get_resources_id(agent_id, path)
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT version FROM coursework.public.versions "
                       f"WHERE resources_id = {resources_id} AND is_actual = True")
        version = cursor.fetchone()[0]
    close(conn)
    return version


def download_folder(login, mac, path, version):
    agent_id = get_agent_id(login, mac)
    resources_id = get_resources_id(agent_id, path)
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT path FROM coursework.public.versions "
                       f"WHERE resources_id = {resources_id} AND version = '{version}'")
        server_path = cursor.fetchone()[0]
    close(conn)
    return codecs.open(server_path, 'rb').read()

# def get_files(login, mac, folder, version):
#     conn = connect()
#     with conn.cursor() as cursor:
#         cursor.execute(f'''
#                     SELECT user_id, folder_id FROM coursework.public.folders WHERE
#                         user_id = '{user_id}' AND
#                         folder_id = '{folder_id}';
#                 ''')
#
#         cursor.execute(f'''
#             SELECT file, edited_at FROM coursework.public.files WHERE
#                 user_id = '{user_id}' AND
#                 folder_id = '{folder_id}';
#         ''')
#         files = cursor.fetchall()
#     close(conn)
#     return get_json(files, 'file', 'edited_at')
