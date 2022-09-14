from Market import db, login_manger
from flask_login import UserMixin

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