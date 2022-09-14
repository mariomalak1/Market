from . import db, login_manger
from flask_login import UserMixin
from datetime import datetime

@login_manger.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable= False)
    password = db.Column(db.String(40), nullable = False)
    phone_num = db.Column(db.String(11), nullable= True)
    salary = db.Column(db.Integer, nullable=True)
    admin = db.Column(db.BOOLEAN, nullable= True, default= False)
    his_money = db.Column(db.Integer, nullable= True, default= 0)

    def __repr__(self):
        return f"User('{self.name}', admin : '{self.admin}', phone number : '{self.phone_num}', salary : '{self.salary}')"

    def IsAdmin(self):
        if self.admin:
            return True
        else:
            return False

class Buyer(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    name = db.Column(db.String(100), nullable= False)
    description = db.Column(db.Text, nullable= True)
    phone_num = db.Column(db.String(11), nullable= True)
    discount = db.Column(db.Integer, nullable= True, default= 0)
    goods = db.relationship('Commodity', backref = "buyer", lazy = True)
    user_created_buyer_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    money_on_him = db.Column(db.Integer, nullable= True, default= 0)
    money_he_pay = db.Column(db.Integer, nullable= True, default= 0)


    def __repr__(self):
        return f"Buyer('{self.name}', '{self.id}', '{self.discount}')"

class Commodity(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    name = db.Column(db.String(200), nullable= False)
    description = db.Column(db.Text, nullable= True)
    quantity = db.Column(db.Integer, nullable= False)
    price = db.Column(db.Integer, nullable= False)
    pay_quantity = db.Column(db.Integer, nullable= False, default= 0)
    date = db.Column(db.DateTime, nullable= False,default = datetime.now)
    buyer_id = db.Column(db.Integer, db.ForeignKey("buyer.id"), nullable = False)
    user_created_good_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return f"Commodity('{self.name}', '{self.quantity}', '{self.price}, '{self.pay_quantity}', '{self.date}')"

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    notification_name = db.Column(db.Text, nullable= True)
    date = db.Column(db.DateTime, nullable= True, default= datetime.now)
    user = db.relationship('User', backref = "user_actions", lazy = True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return f"Notification('{self.notification_name}', Date: '{self.date}', User id: '{self.user_id}')"

