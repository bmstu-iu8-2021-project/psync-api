from db_control.init import connect, close


def auth(login, password):
    # return user_db.session.query(Users).filter(and_(
    #     Users.login == login,
    #     Users.password == password,
    # )).count() == 1
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT * FROM coursework.public.persons WHERE login = '{login}' AND password = '{password}';")
        user = cursor.fetchone()
    close(conn)
    return bool(user)


def find_login(login):
    # return str(int(user_db.session.query(Users).filter_by(login=login).count() != 0))
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT email FROM coursework.public.persons WHERE login = '{login}';")
        email = cursor.fetchone()
    close(conn)
    return str(int(bool(email)))


def find_email(email):
    # return str(int(user_db.session.query(Users).filter_by(email=email).count() != 0))
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT login FROM coursework.public.persons WHERE email = '{email}';")
        login = cursor.fetchone()
    close(conn)
    return str(int(bool(login)))


def get_email(login):
    # usr = user_db.session.query(Users).filter_by(login=login).one()
    # return usr.mail
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT email FROM coursework.public.persons WHERE login = '{login}';")
        email = cursor.fetchone()
    close(conn)
    return email[0]


def get_password(login):
    # usr = user_db.session.query(Users).filter_by(login=login).one()
    # return usr.password
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT password FROM coursework.public.persons WHERE login = '{login}';")
        password = cursor.fetchone()
    close(conn)
    return password[0]


def add_user(login, email, password):
    # user = Users(login=login, mail=email, password=password)
    # user_db.session.add(user)
    # user_db.session.commit()
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f"INSERT INTO coursework.public.persons VALUES('{login}', '{email}', '{password}');")
    close(conn)


def delete_user(login):
    # user_db.session.query(Users).filter_by(login=login).delete()
    # user_db.session.query(Folders).filter_by(login=login).delete()
    # user_db.session.query(Files).filter_by(login=login).delete()
    # user_db.session.commit()
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f"DELETE FROM coursework.public.persons WHERE login = '{login}';")
        cursor.execute(f"SELECT user_id FROM coursework.public.folders WHERE login = '{login}';")
        # user_id = set([i[0] for i in cursor.fetchall()])
        # # cursor.execute('SELECT * FROM coursework.public.folders WHERE user_id IN %s', (tuple(user_id),))
        # # print(cursor.fetchall())
        # cursor.execute(f"DELETE FROM coursework.public.files WHERE user_id IN %s;", (tuple(user_id),))
        # cursor.execute(f"DELETE FROM coursework.public.folders WHERE login = '{login}';")
    close(conn)


def change(login, field, new_value):
    # usr = Users.query.filter_by(login=login).first()
    # if field == 'mail':
    #     usr.mail = new_value
    # elif field == 'password':
    #     usr.password = new_value
    # user_db.session.commit()
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f"UPDATE coursework.public.persons SET {field} = '{new_value}' WHERE login = '{login}'")
    close(conn)


# add version
def add_folder(login, mac, folder_path, version):
    # count = user_db.session.query(Folders).filter_by(login=login).count()
    # row_id = 0
    # if user_db.session.query(Folders).count() != 0:
    #     row_id = user_db.session.query(Folders, func.max(Folders.id)).one()[1] + 1
    # fld = Folders(
    #     id=row_id,
    #     login=login,
    #     mac=mac,
    #     folder_path=folder_path,
    #     folder_version=version,
    #     folder_id=count
    # )
    # user_db.session.add(fld)
    # user_db.session.commit()
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            SELECT user_id FROM coursework.public.folders WHERE 
                login = '{login}' AND 
                mac = '{mac}';
        ''')
        user_id = cursor.fetchone()
        if user_id is None:
            cursor.execute(f"SELECT MAX(user_id) FROM coursework.public.folders")
            user_id = cursor.fetchone()
            if user_id[0] is None:
                user_id = 0
            else:
                user_id = user_id[0] + 1
        else:
            user_id = user_id[0]

        cursor.execute(f'''
            SELECT folder_id FROM coursework.public.folders WHERE 
                login = '{login}' AND 
                mac = '{mac}' AND
                folder = '{folder_path}' AND 
                version = '{version}';
        ''')
        folder_id = cursor.fetchone()
        if folder_id is None:
            cursor.execute(f"SELECT MAX(folder_id) FROM coursework.public.folders")
            folder_id = cursor.fetchone()
            if folder_id[0] is None:
                folder_id = 0
            else:
                folder_id = folder_id[0] + 1
        else:
            folder_id = folder_id[0]

        cursor.execute(f'''
            INSERT INTO coursework.public.folders VALUES(
                '{login}', 
                '{mac}', 
                {user_id}, 
                '{folder_path}', 
                '{version}', 
                {folder_id}
        );''')
    close(conn)


def add_files(login, mac, folder_path, file_path, edited_at, version):
    # row_id = 0
    # if user_db.session.query(Files).count() != 0:
    #     row_id = user_db.session.query(Files, func.max(Files.id)).one()[1] + 1
    # fls = Files(
    #     id=row_id,
    #     login=login,
    #     mac=mac,
    #     folder_path=folder_path,
    #     filename=file_path,
    #     edited_at=edited_at,
    #     file_version=version
    # )
    # user_db.session.add(fls)
    # user_db.session.commit()
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
            SELECT user_id FROM coursework.public.folders WHERE login = '{login}' AND mac = '{mac}';
        ''')
        user_id = cursor.fetchone()
        user_id = user_id[0]
        cursor.execute(f'''
            SELECT folder_id FROM coursework.public.folders WHERE folder = '{folder_path}' AND version = '{version}';
        ''')
        folder_id = cursor.fetchone()
        folder_id = folder_id[0]

        cursor.execute(f'''
            INSERT INTO coursework.public.files VALUES( 
                {user_id}, 
                {folder_id},
                '{file_path}',
                {edited_at}
        );''')
    close(conn)


# delete version
def delete_folder(login, mac, folder_path, version):
    # user_db.session.query(Folders).filter(and_(
    #     Folders.login == login,
    #     Folders.mac == mac,
    #     Folders.folder_path == folder_path,
    #     Folders.folder_version == version
    # )).delete()
    # user_db.session.query(Files).filter(and_(
    #     Files.login == login,
    #     Files.mac == mac,
    #     Files.folder_path == folder_path,
    #     Files.file_version == version
    # )).delete()
    # user_db.session.commit()
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
                SELECT user_id, folder_id FROM coursework.public.folders WHERE 
                    login = '{login}' AND 
                    mac = '{mac}' AND 
                    folder = '{folder_path}' AND
                    version = '{version}';
            ''')
        folder_id = cursor.fetchall()
        folder_id, user_id = folder_id[0]

        cursor.execute(f'''
            DELETE FROM coursework.public.files WHERE user_id = '{user_id}' AND folder_id = '{folder_id}';
        ''')
        cursor.execute(f'''
            DELETE FROM coursework.public.folders WHERE user_id = '{user_id}' AND folder_id = '{folder_id}';
        ''')
    close(conn)


def find_version(login, mac, folder_path, version):
    # return str(int(user_db.session.query(Folders).filter_by(
    #     login=login,
    #     mac=mac,
    #     folder_path=folder_path,
    #     folder_version=version
    # ).count() != 0))
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f'''
                    SELECT * FROM coursework.public.folders WHERE 
                        login = '{login}' AND 
                        mac = '{mac}' AND 
                        folder = '{folder_path}' AND
                        version = '{version}';
                ''')
        get = cursor.fetchall()
    close(conn)
    return bool(get)
