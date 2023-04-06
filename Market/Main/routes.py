from flask import render_template, Blueprint, request
from flask_login import login_required
from Market import db
from Market.User.routes import current_user_is_admin, current_user
from Market.Main.models import Notification
from Market.Buyer.models import Buyer
# application's code here

main = Blueprint("main", __name__)

@main.route('/')
@main.route("/home")
@login_required
def home():
    n = Notification(notification_name=f"""نم دخول المستخدم {current_user.name} الي الصفحة الرئيسية""", user_id=current_user.id)
    db.session.add(n)
    db.session.commit()
    return render_template("main/home.html", title ="home", page_title ="")

@main.route("/admin_panel", methods = ["POST", "GET"], endpoint= "admin_panel")
@current_user_is_admin
def admin_panel():
    buyers = Buyer.query.all()
    total_money_in_market = 0
    for buyer in buyers:
        total_money_in_market += buyer.money_on_him
    n = Notification(notification_name=f"""نم دخول المستخدم {current_user.name} الي صفحة الادارة و التحكم""", user_id=current_user.id)
    db.session.add(n)
    db.session.commit()

    last_notification = []
    n = Notification.query.order_by(Notification.date.desc()).all()
    for i in range(6):
        last_notification.append(n[i])
    return render_template("main/admin_panel.html", page_title ="صفحة الادارة و التحكم", total_money_in_market = total_money_in_market, last_notification = last_notification )

@main.route("/display_all_notification", endpoint= "display_all_notification")
@current_user_is_admin
def display_all_notification():
    page = request.args.get("page", 1, type=int)
    n = Notification.query.order_by(Notification.date.desc()).paginate(page=page, per_page=20)
    return render_template("main/display_all_notification.html", last_notification = n)