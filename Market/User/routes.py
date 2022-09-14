from Market import db
from flask import render_template, redirect, url_for, flash, request, Blueprint
from Market.User.forms import *
from Market.User.models import User
from Market.Main.models import Notification
from flask_login import current_user, login_required, login_user, logout_user


user = Blueprint("user", __name__)

# User Routes

def current_user_is_admin(func):
    def checkit():
        try:
            user_ = User.query.filter_by(id = current_user.id).first()
        except:
            flash("انت لم تسجل بعد", "warning")
            return redirect(url_for("user.login"))
        else:
            if user_:
                if user_.IsAdmin():
                    return func()
                else:
                    flash("انت لست مسؤل", "warning")
                    return redirect(url_for("user.login"))
            else:
                flash("انت لم تسجل بعد", "warning")
                return redirect(url_for("user.login"))
    return checkit


@user.route("/login", methods = ["post", "get"])
def login():
    loginform = LoginForm()
    if loginform.validate_on_submit():
        user_ = User.query.filter_by(name = loginform.username.data).first()
        if user_ and by.check_password_hash(user_.password, loginform.password.data):
            login_user(user_, remember= loginform.remember_me.data)
            next_page = request.args.get('next')
            n = Notification(notification_name=f"تم تسجيل دخول {current_user.name}",user_id=current_user.id)
            db.session.add(n)
            db.session.commit()
            flash(f"تم تسجيل دخول {current_user.name}", "info")
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for("main.home"))
        else:
            flash("برجاء ادخال بيانات صحيحة", "danger")
    return render_template("user_templates/login_page.html", form_login= loginform, title="Login", page_title ="")


@user.route("/signup", methods = ["post", "get"], endpoint='signup')
@current_user_is_admin
def signup():
    register_form = RegistrationFrom()
    if register_form.validate_on_submit():
        hashed_password = by.generate_password_hash(register_form.password.data).decode('utf-8')
        user_registration = User(name= register_form.username.data, password = hashed_password,
                                 phone_num = register_form.phone_num.data,
                                 salary = register_form.salary.data,
                                 admin = register_form.admin.data)
        n = Notification(notification_name=f"تم عمل مستخدم جديد {user_registration.name} بواسطة {current_user.name}", user_id=current_user.id)
        db.session.add(user_registration)
        db.session.add(n)
        db.session.commit()

        flash("تم عمل مستخدم جديد بنجاح", "success")
        return redirect(url_for("main.home"))
    else:
        return render_template("user_templates/register.html", form = register_form, title ="Registration")

@user.route("/logout", endpoint= "logout")
def logout():
    n = Notification(notification_name=f"تم تسجيل خروج {current_user.name}", user_id=current_user.id)
    db.session.add(n)
    db.session.commit()
    logout_user()
    return redirect(url_for("user.login"))

@user.route("/change_password", methods = ["POST", "GET"], endpoint= "change_password")
@login_required
def change_password():
    form = ChangePasswordUserForm()
    if form.validate_on_submit():
        if by.check_password_hash(current_user.password, form.old_password.data):
            current_user.password = by.generate_password_hash(form.password.data).decode('utf-8')
            n = Notification(notification_name=f"تم تغير الرقم السري للمستخدم {current_user.name}", user_id=current_user.id)
            db.session.add(n)
            db.session.commit()
            flash("تم تغير الرقم السري بنجاح","success")
            db.session.commit()
            return redirect("home")
    return render_template("user_templates/change_password_user.html", form = form, page_title ="")

@user.route("/change_user_information", methods = ["POST", "GET"], endpoint= "change_user_information")
@current_user_is_admin
def change_user_information():
    form = ChangeUserInformationForm()
    if form.validate_on_submit():
        user_ = User.query.filter_by(name = form.username_select.data).first()
        if user_.admin and user_ != current_user:
            flash("هذا المستخدم مسؤل لا يمكنك تغير بيناته", "warning")
            return redirect(url_for("user.user_display"))
        else:
            user_.name = form.username.data
            user_.phone_num = form.phone_num.data
            user_.salary = form.salary.data
            user_.admin = form.admin.data
            n = Notification(notification_name=f"تم تغير بيانات المستخدم {user_.name} بواسطة {current_user.name}", user_id=current_user.id)
            db.session.add(n)
            db.session.commit()
            flash("تم التغير بنجاح", "success")
            return redirect(url_for("main.home"))
    return render_template("user_templates/change_user_information_by_admin.html", form = form)


@user.route("/admin_panel", methods = ["POST", "GET"], endpoint= "admin_panel")
@current_user_is_admin
def admin_panel():
    return render_template("buyer_templates/admin_panel.html", page_title ="صفحة الادارة و التحكم")

@user.route("/user_display", endpoint= "user_display")
@current_user_is_admin
def user_display():
    users = User.query.all()
    list_of_users = []
    for i in range(users[-1].id):
        list_user = [users[i].name, users[i].admin, users[i].salary, users[i].phone_num, i+1, users[i].id]
        list_of_users.append(list_user)
    return render_template("user_templates/user_display.html", users = list_of_users, length= len(list_of_users), page_title ="عرض المستخدمين")


@user.route("/user/<int:user_id>", endpoint="user_info", methods = ["POST", "GET"])
def user_info(user_id):
    user_data = User.query.get_or_404(user_id)
    if user_data:
        if user_data.admin and user_data != current_user:
            flash("هذا المستخدم مسؤل لا يمكنك تغير بيناته", "warning")
            return redirect(url_for("user.user_display"))
        else:
            form = ChangeSpecificUserInformationForm()
            try:
                user_ = User.query.filter_by(id=current_user.id).first()
            except:
                flash("انت لم تسجل بعد", "warning")
                return redirect(url_for("user.login"))
            else:
                form.admin.data = user_data.admin
                if user_:
                    if user_.IsAdmin():
                        if form.validate_on_submit():

                            user_data.salary = form.salary.data
                            user_data.name = form.username.data
                            user_data.admin = form.admin.data
                            user_data.phone_num = form.phone_num.data
                            db.session.commit()
                            flash("نم تغير بيانات المستخدم بنجاح", "success")
                            return redirect(url_for("user.user_display"))
                        return render_template("user_templates/changespecificuserinformation.html", user= user_data, form = form, page_title ="صفحة المستخدم")
                    else:
                        flash("انت لست مسؤل", "warning")
                        return redirect(url_for("user.login"))
                else:
                    flash("انت لم تسجل بعد", "warning")
                    return redirect(url_for("user.login"))