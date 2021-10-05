from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databases/users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '80gp3beqsazmdl3wy1j617vho'
user_db = SQLAlchemy(app)


class Users(user_db.Model):
    __tablename__ = 'Users'
    login = user_db.Column(user_db.String(100), primary_key=True, nullable=False)
    mail = user_db.Column(user_db.String(100), unique=True, nullable=False)
    password = user_db.Column(user_db.String(100), nullable=False)


class Folders(user_db.Model):
    __tablename__ = 'Folders'
    id = user_db.Column(user_db.Integer, primary_key=True)
    login = user_db.Column(user_db.String(100), user_db.ForeignKey('Users.login'))
    mac = user_db.Column(user_db.String(50), nullable=False)
    folder_path = user_db.Column(user_db.String(200), nullable=False)
    folder_version = user_db.Column(user_db.String(50), default='')
    folder_id = user_db.Column(user_db.Integer, default=-1)


class Files(user_db.Model):
    __tablename__ = 'Files'
    id = user_db.Column(user_db.Integer, primary_key=True)
    login = user_db.Column(user_db.String(100), user_db.ForeignKey('Folders.login'))
    mac = user_db.Column(user_db.String(50), user_db.ForeignKey('Folders.mac'))
    folder_path = user_db.Column(user_db.String(200), user_db.ForeignKey('Folders.folder_path'))
    filename = user_db.Column(user_db.String(400), nullable=False)
    edited_at = user_db.Column(user_db.Float, nullable=False)
    file_version = user_db.Column(user_db.String(50), default='')
