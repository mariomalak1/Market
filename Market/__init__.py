from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt


app = Flask(__name__)
db = SQLAlchemy(app)
by = Bcrypt(app)
login_manger = LoginManager(app)
                          # function name  of routes
login_manger.login_view = 'user.login'

login_manger.login_message_category = 'warning'
login_manger.login_message = "سجل الدخول اولا"
app.config['SECRET_KEY'] = "1e6fcc6160a5d633efd78b334c5416gd"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///MarketApp.db"

from Market.User.routes import user
from Market.Buyer.routes import buyer
from Market.Main.routes import main
from Market.Product.routes import product

app.register_blueprint(user)
app.register_blueprint(buyer)
app.register_blueprint(product)
app.register_blueprint(main)