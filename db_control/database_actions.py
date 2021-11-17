import codecs
import json
import os
import bcrypt
import datetime

from db_control.init import connect, close
from db_control import files_actions
from server_control.init import app


def auth(login, password, mac):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            SELECT password, id
            FROM coursework.public.persons
            WHERE login = '{login}';
        ''')
        pack = cursor.fetchone()
        if pack is None:
            close(conn)
            return False
        pw, person_id = pack
        if pw:
            if bcrypt.checkpw(password.encode('UTF-8'), pw.encode('UTF-8')):
                cursor.execute(f'''
                    SELECT id 
                    FROM coursework.public.hosts 
                    WHERE mac = '{mac}';
                ''')
                host_id = cursor.fetchone()
                if host_id is None:
                    host_id = add_host(mac)
                else:
                    host_id = host_id[0]
                cursor.execute(f'''
                    SELECT id 
                    FROM coursework.public.agent 
                    WHERE person_id = {person_id} AND host_id = {host_id};
                ''')
                agent_id = cursor.fetchone()
                if agent_id is None:
                    cursor.execute(f'''
                        INSERT INTO coursework.public.agent (person_id, host_id) 
                        VALUES({person_id}, {host_id});
                    ''')
                close(conn)
                return True
    close(conn)
    return False


def find_login(login):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            SELECT email 
            FROM coursework.public.persons 
            WHERE login = '{login}';
        ''')
        email = cursor.fetchone()
    close(conn)
    return str(email is None)


def find_email(email):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            SELECT login 
            FROM coursework.public.persons 
            WHERE email = '{email}';
        ''')
        login = cursor.fetchone()
    close(conn)
    return str(login is None)


def get_email(login):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            SELECT email 
            FROM coursework.public.persons 
            WHERE login = '{login}';
        ''')
        email = cursor.fetchone()
    close(conn)
    return email[0]


def get_password(login):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            SELECT password 
            FROM coursework.public.persons 
            WHERE login = '{login}';
        ''')
        password = cursor.fetchone()
    close(conn)
    return password[0]


def get_person_id(login):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            SELECT id 
            FROM coursework.public.persons 
            WHERE login = '{login}';
        ''')
        person_id = cursor.fetchone()[0]
    close(conn)
    return person_id


def get_host_id(mac):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            SELECT id 
            FROM coursework.public.hosts 
            WHERE mac = '{mac}';
        ''')
        host_id = cursor.fetchone()[0]
    close(conn)
    return host_id


def get_agent_id(login, mac):
    person_id = get_person_id(login)
    host_id = get_host_id(mac)
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            SELECT id 
            FROM coursework.public.agent 
            WHERE person_id = {person_id} AND host_id = {host_id};
        ''')
        agent_id = cursor.fetchone()[0]
    close(conn)
    return agent_id


def get_resources_id(agent_id, path):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            SELECT id 
            FROM coursework.public.resources 
            WHERE agent_id = {agent_id} AND path = '{path}';
        ''')
        resources_id = cursor.fetchone()[0]
    close(conn)
    return resources_id


def change(login, field, new_value):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            UPDATE coursework.public.persons
            SET {field} = '{new_value}'
            WHERE login = '{login}';
        ''')
    close(conn)


def add_host(mac):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            INSERT INTO coursework.public.hosts (mac) 
            VALUES('{mac}');
        ''')
        cursor.execute(f'''
            SELECT id 
            FROM coursework.public.hosts 
            WHERE mac = '{mac}';
        ''')
        host_id = cursor.fetchone()[0]
    close(conn)
    return host_id


def add_user(login, mac, email, password):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            INSERT INTO coursework.public.persons (login, email, password) 
            VALUES('{login}', '{email}', '{password}');
        ''')
        cursor.execute(f'''
            INSERT INTO coursework.public.hosts (mac)
            VALUES ('{mac}')
            ON CONFLICT DO NOTHING;
        ''')
        cursor.execute(f'''
            SELECT id 
            FROM coursework.public.persons 
            WHERE login = '{login}';
        ''')
        person_id = int(cursor.fetchone()[0])
        cursor.execute(f'''
            SELECT id 
            FROM coursework.public.hosts 
            WHERE mac = '{mac}';
        ''')
        host_id = int(cursor.fetchone()[0])
        cursor.execute(f'''
            INSERT INTO coursework.public.agent (person_id, host_id) 
            VALUES({person_id}, {host_id});
        ''')
    close(conn)


def delete_user(login):
    person_id = get_person_id(login)
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            SELECT id 
            FROM coursework.public.agent 
            WHERE person_id = {person_id};
        ''')
        agent_ids = [i[0] for i in cursor.fetchall()]
        for agent_id in agent_ids:
            cursor.execute(f'''
                SELECT id 
                FROM coursework.public.resources 
                WHERE agent_id = {agent_id};
            ''')
            res_ids = [i[0] for i in cursor.fetchall()]
            for res_id in res_ids:
                cursor.execute(f'''
                    SELECT path 
                    FROM coursework.public.versions 
                    WHERE resource_id = {res_id};
                ''')
                [os.remove(i[0]) for i in cursor.fetchall()]
        cursor.execute(f'''
            DELETE
            FROM coursework.public.persons
            WHERE login = '{login}';
        ''')
    close(conn)


def find_version(login, mac, folder_path, version):
    agent_id = get_agent_id(login, mac)
    get = None
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            SELECT id 
            FROM coursework.public.resources 
            WHERE agent_id = {agent_id} AND path = '{folder_path}';
        ''')
        resources_id = cursor.fetchone()
        if resources_id is not None:
            cursor.execute(f'''
                SELECT version 
                FROM coursework.public.versions 
                WHERE resource_id = {resources_id[0]} AND version = '{version}';
            ''')
            get = cursor.fetchone()
    close(conn)
    return str(get is None)


def add_version(login, mac, folder_path, version, is_actual):
    agent_id = get_agent_id(login, mac)
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            SELECT id 
            FROM coursework.public.resources 
            WHERE agent_id = {agent_id} AND path = '{folder_path}';
        ''')
        if cursor.fetchone() is None:
            cursor.execute(f'''
                INSERT INTO coursework.public.resources (agent_id, path) 
                VALUES({agent_id}, '{folder_path}');
            ''')
        cursor.execute(f'''
            SELECT id 
            FROM coursework.public.resources 
            WHERE agent_id = {agent_id} AND path = '{folder_path}';
        ''')
        res_id = int(cursor.fetchone()[0])

        path = os.path.join(app.config['UPLOAD_FOLDER'], '_'.join([login, folder_path[folder_path.rfind('/') + 1:],
                                                                   version]) + '.zip')
        cursor.execute(f'''
        INSERT INTO coursework.public.versions (resource_id, version, created_at, is_actual, path) 
        VALUES({res_id}, '{version}', '{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}', {is_actual}, '{path}');
        ''')
    close(conn)


def update_version(login, mac, path_file, version):
    agent_id = get_agent_id(login, mac)
    resource_id = get_resources_id(agent_id, path_file)
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            UPDATE coursework.public.versions
            SET created_at = '{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}'
            WHERE resource_id = {resource_id} and version = '{version}';            
        ''')
    close(conn)


def download_folder(login, mac, path, version=None):
    agent_id = get_agent_id(login, mac)
    resources_id = get_resources_id(agent_id, path)
    conn = connect()
    with conn.cursor() as cursor:
        if version is not None:
            cursor.execute(f'''
                SELECT path 
                FROM coursework.public.versions 
                WHERE resource_id = {resources_id} AND version = '{version}';
            ''')
        else:
            cursor.execute(f'''
                SELECT path
                FROM coursework.public.versions
                WHERE resource_id = {resources_id} AND is_actual = True;
            ''')
        server_path = cursor.fetchone()[0]
    close(conn)
    return codecs.open(server_path, 'rb').read()


def delete_version(login, mac, folder_path, version):
    agent_id = get_agent_id(login, mac)
    resource_id = get_resources_id(agent_id, folder_path)
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            SELECT path 
            FROM coursework.public.versions 
            WHERE resource_id = {resource_id} AND version = '{version}';
        ''')
        path = cursor.fetchone()[0]
        cursor.execute(f'''
            DELETE 
            FROM coursework.public.versions 
            WHERE resource_id = {resource_id} AND version = '{version}';
        ''')
        cursor.execute(f'''
            SELECT id 
            FROM coursework.public.versions 
            WHERE resource_id = {resource_id};
        ''')
        if cursor.fetchone() is None:
            cursor.execute(f'''
                DELETE 
                FROM coursework.public.resources 
                WHERE agent_id = {agent_id} AND path = '{folder_path}';
            ''')
    close(conn)
    return path


def make_actual(login, mac, path, version):
    agent_id = get_agent_id(login, mac)
    resource_id = get_resources_id(agent_id, path)
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            UPDATE coursework.public.versions 
            SET is_actual = False 
            WHERE resource_id = {resource_id};
        ''')
        cursor.execute(f'''
            UPDATE coursework.public.versions 
            SET is_actual = True 
            WHERE resource_id = {resource_id} AND version = '{version}';
        ''')
    close(conn)


def make_no_actual(login, mac, path):
    agent_id = get_agent_id(login, mac)
    resource_id = get_resources_id(agent_id, path)
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            UPDATE coursework.public.versions 
            SET is_actual = False 
            WHERE resource_id = {resource_id};
        ''')
        cursor.execute(f'''
            DELETE
            FROM coursework.public.replica_set
            WHERE current_resource_id = {resource_id} OR other_resource_id = {resource_id};
        ''')
    close(conn)


def get_folders(login, mac):
    agent_id = get_agent_id(login, mac)
    folders = []
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            SELECT id, path 
            FROM coursework.public.resources 
            WHERE agent_id = {agent_id};
        ''')
        resources_info = cursor.fetchall()
        for pair in resources_info:
            cursor.execute(f'''
                SELECT version, created_at, is_actual 
                FROM coursework.public.versions 
                WHERE resource_id = {pair[0]};
            ''')
            version_info = cursor.fetchall()
            for trinity in version_info:
                folders.append({
                    'folder': pair[1],
                    'version': trinity[0],
                    'created_at': str(trinity[1]),
                    'is_actual': trinity[2]
                })
    close(conn)
    return json.dumps(folders)


def get_actual_version(login, mac, path):
    agent_id = get_agent_id(login, mac)
    resources_id = get_resources_id(agent_id, path)
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            SELECT version 
            FROM coursework.public.versions 
            WHERE resource_id = {resources_id} AND is_actual = True;
        ''')
        version = cursor.fetchone()
    close(conn)
    if version is not None:
        return version[0]
    else:
        return version


def get_difference(data):
    agent_id = get_agent_id(data['login'], data['mac'])
    to_change = {'folder': []}
    conn = connect()
    with conn.cursor() as cursor:
        for folder in data['folder']:
            resource_id = get_resources_id(agent_id, folder['name'])
            cursor.execute(f'''
                SELECT path 
                FROM coursework.public.versions
                WHERE resource_id = {resource_id};
            ''')
            server_path = cursor.fetchone()[0]
            if not files_actions.is_difference(server_path=server_path, content=folder['files']):
                to_change['folder'].append(folder['name'])
    close(conn)
    return json.dumps(to_change)


def synchronize(current, other):
    current_agent_id = get_agent_id(current[0], current[1])
    other_agent_id = get_agent_id(other[0], other[1])
    current_resource_id = get_resources_id(current_agent_id, current[2])
    other_resource_id = get_resources_id(other_agent_id, other[2])
    if current[0] != other[0]:
        conn = connect()
        with conn.cursor() as cursor:
            cursor.execute(f'''
                SELECT id 
                FROM coursework.public.replica_set 
                WHERE current_resource_id = {other_resource_id} AND other_resource_id = {current_resource_id};
            ''')
            if cursor.fetchone() is None:
                cursor.execute(f'''
                    INSERT INTO coursework.public.replica_set (current_resource_id, other_resource_id) 
                    VALUES({current_resource_id}, {other_resource_id});
                ''')
        close(conn)


def synchronize_folder(current_login, current_mac, current_folder, other_login, other_folder):
    current_agent_id = get_agent_id(current_login, current_mac)
    current_resource_id = get_resources_id(current_agent_id, current_folder)
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            SELECT path
            FROM coursework.public.versions
            WHERE resource_id = {current_resource_id};
        ''')
        current_pair = (cursor.fetchone()[0], current_folder[current_folder.find('/') + 1:])
        other_pair = [None, other_folder[other_folder.find('/') + 1:]]
        cursor.execute(f'''
            SELECT coursework.public.agent.id
            FROM coursework.public.agent
                     JOIN coursework.public.persons ON coursework.public.persons.id = coursework.public.agent.person_id
            WHERE login = '{other_login}';
        ''')
        other_agents_id = [i[0] for i in cursor.fetchall()]
        for other_agent_id in other_agents_id:
            cursor.execute(f'''
                SELECT coursework.public.versions.path
                FROM coursework.public.versions
                         JOIN coursework.public.resources ON coursework.public.resources.id = coursework.public.versions.resource_id
                WHERE agent_id = {other_agent_id} AND coursework.public.resources.path = '{other_folder}';
            ''')
            other_version_path = cursor.fetchone()
            if other_version_path is not None:
                other_pair[0] = other_version_path[0]
    close(conn)
    other_pair = tuple(other_pair)
    # print(current_pair, other_pair, sep='\n')
    files_actions.merge(current_pair, other_pair)


def terminate_sync(current_login, other_id, current_folder, other_folder, current_mac):
    current_agent_id = get_agent_id(current_login, current_mac)
    current_resource_id = get_resources_id(current_agent_id, current_folder)
    other_resource_id = get_resources_id(other_id, other_folder)
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            DELETE
            FROM coursework.public.replica_set
            WHERE (current_resource_id = {current_resource_id} AND other_resource_id = {other_resource_id})
               OR (current_resource_id = {other_resource_id} AND other_resource_id = {current_resource_id});
        ''')
    close(conn)


def get_pairs_resource_id(login, mac):
    agent_id = get_agent_id(login, mac)
    other_resources_id = []
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            SELECT id
            FROM coursework.public.resources
            WHERE agent_id = {agent_id};
        ''')
        result = cursor.fetchall()
        if result is not None:
            resources_id = [i[0] for i in result]
            for resource_id in resources_id:
                cursor.execute(f'''
                    SELECT current_resource_id
                    FROM coursework.public.replica_set
                    WHERE other_resource_id = {resource_id};
                ''')
                result = cursor.fetchall()
                if result is not None:
                    other_resources_id += [tuple([resource_id, i[0]]) for i in result]

                cursor.execute(f'''
                    SELECT other_resource_id
                    FROM coursework.public.replica_set
                    WHERE current_resource_id = {resource_id};
                ''')
                result = cursor.fetchall()
                if result is not None:
                    other_resources_id += [tuple([resource_id, i[0]]) for i in result]
    close(conn)
    return other_resources_id


def get_synchronized(login, mac):
    pairs = get_pairs_resource_id(login, mac)
    table = []
    conn = connect()
    with conn.cursor() as cursor:
        for pair in pairs:
            cursor.execute(f'''
                SELECT coursework.public.resources.path, coursework.public.versions.created_at
                FROM coursework.public.resources
                         JOIN coursework.public.versions ON coursework.public.resources.id = coursework.public.versions.resource_id
                WHERE coursework.public.resources.id = {pair[0]};
            ''')
            current_path, current_time = cursor.fetchone()
            cursor.execute(f'''
                SELECT agent_id, path
                FROM coursework.public.resources
                WHERE id = {pair[1]};
            ''')
            other_id, other_folder = cursor.fetchone()
            cursor.execute(f'''
                SELECT login
                FROM coursework.public.persons
                         JOIN coursework.public.agent ON coursework.public.persons.id = coursework.public.agent.person_id
                WHERE coursework.public.agent.id = {other_id};
            ''')
            other_login = cursor.fetchone()[0]
            table.append({
                'other_id': str(other_id),
                'other_login': other_login,
                'current_folder': current_path,
                'other_folder': other_folder,
                'current_time': str(current_time)
            })
    close(conn)
    return json.dumps(table)


def check_synchronized(login, mac):
    pairs = get_pairs_resource_id(login, mac)
    table = []
    conn = connect()
    with conn.cursor() as cursor:
        for pair in pairs:
            cursor.execute(f'''
                SELECT coursework.public.versions.path, coursework.public.resources.path
                FROM coursework.public.resources
                         JOIN coursework.public.versions ON coursework.public.resources.id = coursework.public.versions.resource_id
                WHERE is_actual = True
                  AND coursework.public.resources.id = {pair[0]};
            ''')
            current_pair = cursor.fetchone()
            cursor.execute(f'''
                SELECT coursework.public.versions.path, coursework.public.resources.path
                FROM coursework.public.resources
                         JOIN coursework.public.versions ON coursework.public.resources.id = coursework.public.versions.resource_id
                WHERE is_actual = True
                  AND coursework.public.resources.id = {pair[1]};
            ''')
            other_pair = cursor.fetchone()
            if not files_actions.compare_archives(
                    current_archive=current_pair,
                    other_archive=other_pair
            ):
                cursor.execute(f'''
                    SELECT agent_id, path
                    FROM coursework.public.resources
                    WHERE id = {pair[1]};
                ''')
                other_id, other_folder = cursor.fetchone()
                cursor.execute(f'''
                    SELECT path
                    FROM coursework.public.resources
                    WHERE id = {pair[0]};
                ''')
                current_path = cursor.fetchone()[0]
                cursor.execute(f'''
                    SELECT login
                    FROM coursework.public.persons
                             JOIN coursework.public.agent ON coursework.public.persons.id = coursework.public.agent.person_id
                    WHERE coursework.public.agent.id = {other_id};
                ''')
                other_login = cursor.fetchone()[0]
                table.append({
                    'other_id': str(other_id),
                    'other_user': other_login,
                    'current_folder': current_path,
                    'other_folder': other_folder
                })
    close(conn)
    return json.dumps(table)
