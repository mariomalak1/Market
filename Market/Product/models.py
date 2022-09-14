from Market import db
from datetime import datetime

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
