import codecs
import json
import os
import bcrypt
import datetime

from db_control.init import connect, close
import files_actions


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
                    cursor.execute(f'''
                        INSERT INTO coursework.public.agent (person_id, host_id) 
                        VALUES({person_id}, {host_id});
                    ''')
                close(conn)
                return True
    close(conn)
    return False


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
        host_id = cursor.fetchone()
    close(conn)
    return host_id


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


def change(login, field, new_value):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            UPDATE coursework.public.persons
            SET {field} = '{new_value}'
            WHERE login = '{login}';
        ''')
    close(conn)


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


# add version
def add_folder(login, mac, folder_path, version, is_actual, path):
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

        cursor.execute(f'''
        INSERT INTO coursework.public.versions (resource_id, version, created_at, is_actual, path) 
        VALUES({res_id}, '{version}', '{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}', {is_actual}, '{path}');
        ''')
    close(conn)


# delete version
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
        if not (resources_id is None):
            cursor.execute(f'''
                SELECT version 
                FROM coursework.public.versions 
                WHERE resource_id = {resources_id[0]} AND version = '{version}';
            ''')
            get = cursor.fetchone()
    close(conn)
    return str(get is None)


# def get_json(output, path, version_info, *args):
#     if output is None or len(output.keys()) == 0:
#         output = dict()
#         for arg in args:
#             output[arg] = list()
#     for row in version_info:
#         output[args[0]].append(path)
#         for arg in args[1:]:
#             output[arg].append(str(row[args[1:].index(arg)]))
#     return output


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
            # folders = get_json(folders, pair[1], version_info, 'folder', 'version', 'created_at', 'is_actual')
            for trinity in version_info:
                folders.append({
                    'folder': pair[1],
                    'version': trinity[0],
                    'created_at': str(trinity[1]),
                    'is_actual': trinity[2]
                })
    close(conn)
    return json.dumps(folders)


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
        version = cursor.fetchone()[0]
    close(conn)
    return version


def download_folder(login, mac, path, version):
    agent_id = get_agent_id(login, mac)
    resources_id = get_resources_id(agent_id, path)
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            SELECT path 
            FROM coursework.public.versions 
            WHERE resource_id = {resources_id} AND version = '{version}';
        ''')
        server_path = cursor.fetchone()[0]
    close(conn)
    return codecs.open(server_path, 'rb').read()


def synchronize(current, other):
    current_agent_id = get_agent_id(current[0], current[1])
    other_agent_id = get_agent_id(other[0], other[1])
    current_resource_id = get_resources_id(current_agent_id, current[2])
    other_resource_id = get_resources_id(other_agent_id, other[2])
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


def get_synchronized(login, mac):
    agent_id = get_agent_id(login, mac)
    conn = connect()
    with conn.cursor() as cursor:
        table = []
        cursor.execute(f'''
            SELECT coursework.public.resources.id
            FROM coursework.public.resources
                     JOIN coursework.public.replica_set ON coursework.public.resources.id = current_resource_id OR
                                                           coursework.public.resources.id = other_resource_id
            WHERE agent_id = {agent_id};
        ''')
        shared_resources_id = [i[0] for i in cursor.fetchall()]
        for resource_id in shared_resources_id:
            cursor.execute(f'''
                SELECT coursework.public.resources.path, coursework.public.versions.created_at
                FROM coursework.public.resources
                         JOIN coursework.public.versions ON coursework.public.resources.id = resource_id
                WHERE is_actual = True
                  AND resource_id = {resource_id};            
            ''')
            current_folder, current_time = cursor.fetchone()

            cursor.execute(f'''
                SELECT current_resource_id
                FROM coursework.public.replica_set
                WHERE other_resource_id = {resource_id}
                UNION
                SELECT other_resource_id
                FROM coursework.public.replica_set
                WHERE current_resource_id = {resource_id};
            ''')
            opposite_resource_id = [i[0] for i in cursor.fetchall()]
            for opp_res_id in opposite_resource_id:
                cursor.execute(f'''
                    SELECT path
                    FROM coursework.public.resources
                    WHERE id = {opp_res_id};        
                ''')
                other_folder = cursor.fetchone()[0]
                cursor.execute(f'''
                    SELECT login
                    FROM coursework.public.persons
                    WHERE id IN
                          (SELECT person_id
                           FROM coursework.public.agent
                           WHERE id IN
                                 (SELECT agent_id FROM coursework.public.resources WHERE id = {opp_res_id}));
                ''')
                other_login = cursor.fetchone()[0]
                table.append({
                    'other_login': other_login,
                    'current_folder': current_folder,
                    'other_folder': other_folder,
                    'current_time': str(current_time)
                })
    close(conn)
    return json.dumps(table)


# def terminate_sync(current_login, other_login, current_folder, other_folder, current_mac):
#     current_agent_id = get_agent_id(current_login, current_mac)
#     current_resource_id = get_resources_id(current_agent_id, current_folder)
#     conn = connect()
#     with conn.cursor() as cursor:
#         cursor.execute(f'''
#         SELECT current_resource_id
#         FROM coursework.public.replica_set
#         WHERE other_resource_id IN (SELECT coursework.public.resources.id
#                                     FROM coursework.public.resources
#                                              JOIN coursework.public.versions ON
#                                                 coursework.public.resources.id = resource_id AND is_actual = True AND
#                                                 agent_id = {current_agent_id})
#         UNION
#         SELECT other_resource_id
#         FROM coursework.public.replica_set
#         WHERE current_resource_id IN (SELECT coursework.public.resources.id
#                                       FROM coursework.public.resources
#                                                JOIN coursework.public.versions ON
#                                                   coursework.public.resources.id = resource_id AND is_actual = True AND
#                                                   agent_id = {current_agent_id});
#         ''')
#         opposite_resource_id = [i[0] for i in cursor.fetchall()]
#         print(opposite_resource_id)
#         for resource_id in opposite_resource_id:
#             cursor.execute(f'''
#                 SELECT login
#                 FROM coursework.public.persons
#                 WHERE id IN
#                       (SELECT person_id
#                        FROM coursework.public.agent
#                        WHERE id IN
#                              (SELECT agent_id FROM coursework.public.resources WHERE id = {resource_id}))
#                 UNION
#                 SELECT path
#                 FROM coursework.public.resources
#                 WHERE id = {resource_id};
#             ''')
#             opposite_info = cursor.fetchall()
#             if opposite_info[0][0] == other_folder and opposite_info[1][0] == other_login:
#                 cursor.execute(f'''
#                     DELETE
#                     FROM coursework.public.replica_set
#                     WHERE (other_resource_id = {resource_id} AND current_resource_id = {current_resource_id})
#                        OR (other_resource_id = {current_resource_id} AND current_resource_id = {resource_id})
#                 ''')
#     close(conn)


def terminate_sync(current_login, other_login, current_folder, other_folder, current_mac):
    agent_id = get_agent_id(current_login, current_mac)
    resource_id = get_resources_id(agent_id, current_folder)
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            SELECT coursework.public.agent.id
            FROM coursework.public.agent
                     JOIN coursework.public.persons ON coursework.public.persons.id = coursework.public.agent.person_id
            WHERE login = '{other_login}';
        ''')
        other_agents_id = [i[0] for i in cursor.fetchall()]
        other_resource_id = -1
        for other_agent_id in other_agents_id:
            cursor.execute(f'''
                SELECT coursework.public.resources.id
                FROM coursework.public.resources
                         JOIN coursework.public.versions ON coursework.public.resources.id = coursework.public.versions.resource_id
                WHERE is_actual = True
                  AND coursework.public.resources.path = '{other_folder}';
            ''')
            output = cursor.fetchone()
            if output is not None:
                other_resource_id = output[0]
        cursor.execute(f'''
            DELETE
            FROM coursework.public.replica_set
            WHERE (current_resource_id = {resource_id} AND other_resource_id = {other_resource_id})
               OR (other_resource_id = {resource_id} AND current_resource_id = {other_resource_id});
        ''')
    close(conn)


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
            if not files_actions.get_difference(
                    server_path=server_path,
                    content=folder['files'],
            ):
                to_change['folder'].append(folder['name'])
    close(conn)
    return json.dumps(to_change)


def check_synchronized(login, mac):
    to_sync = {'items': []}
    agent_id = get_agent_id(login, mac)
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            SELECT current_resource_id, other_resource_id
            FROM coursework.public.replica_set
                     JOIN coursework.public.resources ON
                        coursework.public.resources.id = current_resource_id OR coursework.public.resources.id = other_resource_id
            WHERE coursework.public.resources.agent_id = {agent_id};
        ''')
        pairs = [list(i) for i in cursor.fetchall()]
        for pair in pairs:
            cursor.execute(f'''
                SELECT path
                FROM coursework.public.resources
                WHERE agent_id = {agent_id} AND id = {pair[0]}
            ''')
            if cursor.fetchone() is None:
                pair[0], pair[1] = pair[1], pair[0]
            # 0 -> current_user
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

            cursor.execute(f'''
                SELECT coursework.public.resources.id
                FROM coursework.public.versions
                         JOIN coursework.public.resources ON coursework.public.resources.id = coursework.public.versions.resource_id
                WHERE coursework.public.versions.path = '{other_pair[1]}'
                  AND agent_id = {agent_id};
            ''')
            if not files_actions.compare_archives(
                    current_archive=current_pair,
                    other_archive=other_pair
            ):
                cursor.execute(f'''
                    SELECT login
                    FROM coursework.public.persons
                             JOIN coursework.public.agent ON coursework.public.persons.id = coursework.public.agent.person_id
                             JOIN coursework.public.resources ON coursework.public.agent.id = coursework.public.resources.agent_id
                             JOIN coursework.public.versions ON coursework.public.resources.id = coursework.public.versions.resource_id
                    WHERE coursework.public.resources.path = '{other_pair[1]}';
                ''')
                to_sync['items'].append({
                    'other_user': cursor.fetchone()[0],
                    'current_folder': current_pair[1],
                    'other_folder': other_pair[1]
                })
    close(conn)
    return json.dumps(to_sync)


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


def terminate_all_sync(login, mac, path):
    agent_id = get_agent_id(login, mac)
    resource_id = get_resources_id(agent_id, path)
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            DELETE
            FROM coursework.public.replica_set
            WHERE current_resource_id = {resource_id} OR other_resource_id = {resource_id};
        ''')
    close(conn)
