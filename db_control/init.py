# from flask_sqlalchemy import SQLAlchemy
# from app_control.init import app
#
# user_db = SQLAlchemy(app)
#
#
# class Users(user_db.Model):
#     __tablename__ = 'Users'
#     login = user_db.Column(user_db.String(100), primary_key=True, nullable=False)
#     mail = user_db.Column(user_db.String(100), unique=True, nullable=False)
#     password = user_db.Column(user_db.String(100), nullable=False)
#
#
# class Folders(user_db.Model):
#     __tablename__ = 'Folders'
#     id = user_db.Column(user_db.Integer, primary_key=True)
#     login = user_db.Column(user_db.String(100), user_db.ForeignKey('Users.login'))
#     mac = user_db.Column(user_db.String(50), nullable=False)
#     folder_path = user_db.Column(user_db.String(200), nullable=False)
#     folder_version = user_db.Column(user_db.String(50), default='')
#     folder_id = user_db.Column(user_db.Integer, default=-1)
#
#
# class Files(user_db.Model):
#     __tablename__ = 'Files'
#     id = user_db.Column(user_db.Integer, primary_key=True)
#     login = user_db.Column(user_db.String(100), user_db.ForeignKey('Folders.login'))
#     mac = user_db.Column(user_db.String(50), user_db.ForeignKey('Folders.mac'))
#     folder_path = user_db.Column(user_db.String(200), user_db.ForeignKey('Folders.folder_path'))
#     filename = user_db.Column(user_db.String(400), nullable=False)
#     edited_at = user_db.Column(user_db.Float, nullable=False)
#     file_version = user_db.Column(user_db.String(50), default='')

import psycopg2
from config import HOST, PORT, USER, PASSWORD, DB_NAME


def connect():
    connection = psycopg2.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        database=DB_NAME
    )
    connection.autocommit = True
    return connection


def create():
    connection = connect()

    with connection.cursor() as cursor:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS persons
            (
                login    varchar(50) NOT NULL PRIMARY KEY,
                email    varchar(50) NOT NULL UNIQUE,
                password varchar(40) NOT NULL
            );
            CREATE TABLE IF NOT EXISTS folders
            (
                login     varchar(50)  NOT NULL,
                mac       varchar(30)  NOT NULL,
                user_id   int          NOT NULL,
                folder    varchar(300) NOT NULL,
                version   varchar(20)  NOT NULL,
                folder_id int          NOT NULL,
                PRIMARY KEY (user_id, folder_id),
                FOREIGN KEY (login) REFERENCES persons (login) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS files
            (
                user_id   int          NOT NULL,
                folder_id int          NOT NULL,
                file      varchar(100) NOT NULL,
                edited_at float        NOT NULL,
                FOREIGN KEY (user_id, folder_id) REFERENCES folders (user_id, folder_id) ON DELETE CASCADE
            );
        ''')
    connection.close()


def close(connection):
    connection.close()
