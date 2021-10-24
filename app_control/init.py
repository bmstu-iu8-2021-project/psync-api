from flask import Flask
from db_control.init import create

app = Flask(__name__)
app.config['SECRET_KEY'] = '80gp3beqsazmdl3wy1j617vho'
app.config['UPLOAD_FOLDER'] = '/home/peter/Study/03_semestr/Coursework/Storage/'
create()
