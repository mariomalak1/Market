from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

app = Flask(__name__)
db = SQLAlchemy(app)
by = Bcrypt(app)
login_manger = LoginManager(app)
                          # function name  of routes
login_manger.login_view = 'login'

login_manger.login_message_category = 'warning'
app.config['SECRET_KEY'] = "1e6fcc6160a5d633efd78b334c5416gd"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///MarketApp.db"

from . import routes
