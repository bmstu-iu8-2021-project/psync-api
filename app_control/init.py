from flask import Flask
from db_control.init import create

# BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
# DATABASE_FOLDER = os.path.join(BASE_FOLDER, 'databases')

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(DATABASE_FOLDER, 'users.db')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '80gp3beqsazmdl3wy1j617vho'
create()
