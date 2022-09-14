from Market import db
from datetime import datetime

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    notification_name = db.Column(db.Text, nullable= True)
    date = db.Column(db.DateTime, nullable= True, default= datetime.now)
    user = db.relationship('User', backref = "user_actions", lazy = True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return f"Notification('{self.notification_name}', Date: '{self.date}', User id: '{self.user_id}')"

