from Market import db

class Buyer(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    name = db.Column(db.String(100), nullable= False)
    description = db.Column(db.Text, nullable= True)
    phone_num = db.Column(db.String(11), nullable= True)
    discount = db.Column(db.Integer, nullable= True, default= 0)
    goods = db.relationship('Commodity', backref = "buyer", lazy = True)
    user_created_buyer_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    money_on_him = db.Column(db.Integer, nullable= True, default= 0)
    last_collection_money = db.Column(db.Integer, nullable= True, default= 0)
    last_collection_date = db.Column(db.DateTime, nullable= True)
    last_collection_user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


    def __repr__(self):
        return f"Buyer('{self.name}', '{self.id}', '{self.discount}')"