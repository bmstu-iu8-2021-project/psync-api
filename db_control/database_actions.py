from sqlalchemy import and_, func

from db_control.init import user_db, Users, Folders, Files


def auth(login, password):
    return user_db.session.query(Users).filter(and_(
        Users.login == login,
        Users.password == password,
    )).count() == 1


def find_login(login):
    return str(int(user_db.session.query(Users).filter_by(login=login).count() != 0))


def find_email(email):
    return str(int(user_db.session.query(Users).filter_by(mail=email).count() != 0))


def get_email(login):
    usr = user_db.session.query(Users).filter_by(login=login).one()
    return usr.mail


def get_password(login):
    usr = user_db.session.query(Users).filter_by(login=login).one()
    return usr.password


def add_user(login, email, password):
    user = Users(login=login, mail=email, password=password)
    user_db.session.add(user)
    user_db.session.commit()


def delete_user(login):
    user_db.session.query(Users).filter_by(login=login).delete()
    user_db.session.query(Folders).filter_by(login=login).delete()
    user_db.session.query(Files).filter_by(login=login).delete()
    user_db.session.commit()


def change(login, field, new_value):
    usr = Users.query.filter_by(login=login).first()
    if field == 'mail':
        usr.mail = new_value
    elif field == 'password':
        usr.password = new_value
    user_db.session.commit()


# add version
def add_folder(login, mac, folder_path, version):
    count = user_db.session.query(Folders).filter_by(login=login).count()
    row_id = 0
    if user_db.session.query(Folders).count() != 0:
        row_id = user_db.session.query(Folders, func.max(Folders.id)).one()[1] + 1
    fld = Folders(
        id=row_id,
        login=login,
        mac=mac,
        folder_path=folder_path,
        folder_version=version,
        folder_id=count
    )
    user_db.session.add(fld)
    user_db.session.commit()


def add_files(login, mac, folder_path, file_path, edited_at, version):
    row_id = 0
    if user_db.session.query(Files).count() != 0:
        row_id = user_db.session.query(Files, func.max(Files.id)).one()[1] + 1
    fls = Files(
        id=row_id,
        login=login,
        mac=mac,
        folder_path=folder_path,
        filename=file_path,
        edited_at=edited_at,
        file_version=version
    )
    user_db.session.add(fls)
    user_db.session.commit()


# delete version
def delete_folder(login, mac, folder_path, version):
    user_db.session.query(Folders).filter(and_(
        Folders.login == login,
        Folders.mac == mac,
        Folders.folder_path == folder_path,
        Folders.folder_version == version
    )).delete()
    user_db.session.query(Files).filter(and_(
        Files.login == login,
        Files.mac == mac,
        Files.folder_path == folder_path,
        Files.file_version == version
    )).delete()
    user_db.session.commit()


def find_version(login, mac, folder_path, version):
    return str(int(user_db.session.query(Folders).filter_by(
        login=login,
        mac=mac,
        folder_path=folder_path,
        folder_version=version
    ).count() != 0))
