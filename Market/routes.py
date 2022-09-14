from . import app, db, by
from flask import render_template, redirect, url_for, flash, request, make_response
from .forms import *
from .models import Buyer, User, Commodity, Notification
from flask_login import login_user, current_user, logout_user, login_required
import pdfkit
# application's code here

@app.route('/')
@app.route("/home")
@login_required
def home():
    return render_template("home.html", title = "home", page_title = "")

@app.route("/make_buyer", methods = ["POST", "GET"])
@login_required
def make_buyer():
    form = MakeBuyerForm()
    if form.validate_on_submit():
        buyer = Buyer(name = form.name.data, description = form.description.data,
                      phone_num = form.phone_num.data,
                      money_on_him = form.money_on_him.data,
                      money_he_pay = form.money_on_him.data,
                      discount = form.discount.data, user_created_buyer_id = current_user.id)
        n = Notification(notification_name = f"تم اضافة مشتري جديد {buyer.name}", user_id = current_user.id)
        db.session.add(buyer)
        db.session.add(n)
        db.session.commit()
        flash("تم اضافة مشتري", "success")
        return redirect(url_for("make_buyer"))
    return render_template("make_buyer.html", title = "make buyer", form = form, page_title = "تسجيل مشتري")

@app.route("/add_products", methods = ["POST", "GET"])
@login_required
def add_products():
    form = ProductForm()
    if form.validate_on_submit():
        buyer = Buyer.query.filter_by(name = form.name_buyer.data).first()
        commodity = Commodity(name = form.name.data, description = form.description.data,
                              quantity = form.quantity.data, price = form.price.data,
                              pay_quantity = form.pay_quantity.data, date = form.date.data, buyer_id = buyer.id,
                              user_created_good_id = current_user.id)
        n = Notification(notification_name=f"تم اضافة منتج جديد ل {buyer.name} بواسطة {current_user.name}", user_id=current_user.id)
        db.session.add(n)
        db.session.add(commodity)
        buyer.money_on_him += (commodity.quantity * commodity.price ) - commodity.pay_quantity
        db.session.commit()
        flash("تم انشاء المنتج بنجاح", "success")
        return redirect(url_for("add_products"))
    list_of_users = Buyer.query.all()
    list_names = []
    for user in list_of_users:
        list_names.append(user.name)
    return render_template("add_products.html", form = form, list_names = list_names, title = "Add products", page_title = "تسجيل منتج")

@app.route("/Account_statement", methods = ["POST", "GET"], endpoint= "account_statement")
@login_required
def account_statement():
    form = AccountStatementForm()
    if form.validate_on_submit():
        buyer = Buyer.query.filter_by(name = form.buyer_name.data).first()
        date_from_day = form.date_from.data.day
        date_from_month = form.date_from.data.month
        date_from_year = form.date_from.data.year
        date_to_day = form.date_to.data.day
        date_to_month = form.date_to.data.month
        date_to_year = form.date_to.data.year
        return redirect(url_for("account_statement_response", buyer_id= buyer.id,
        date_from_day = date_from_day, date_from_month = date_from_month, date_from_year = date_from_year,
        date_to_day = date_to_day, date_to_month = date_to_month, date_to_year = date_to_year))
    list_of_users = Buyer.query.all()
    list_names = []
    for user in list_of_users:
        list_names.append(user.name)
    return render_template("account_statement.html", list_names = list_names, form = form, page_title = "كشف حساب")


@app.route("/Account_statement_response/<int:buyer_id>/<int:date_from_day>/<int:date_from_month>/"
           "<int:date_from_year>/<int:date_to_day>/<int:date_to_month>/<int:date_to_year>",
           methods = ["POST", "GET"], endpoint="account_statement_response")
@login_required
def account_statement_response(buyer_id, date_from_day, date_from_month, date_from_year, date_to_day, date_to_month, date_to_year):
    date_from = datetime(date_from_year, date_from_month, date_from_day)
    date_to = datetime(date_to_year, date_to_month, date_to_day)
    buyer = Buyer.query.get_or_404(buyer_id)
    user = User.query.filter_by(id = buyer.user_created_buyer_id).first()
    list_buyer_products = []
    counter = 0
    for product in buyer.goods:
        if date_from <= product.date <= date_to:
            counter += 1
            list_product = [counter, product, buyer, user]
            list_buyer_products.append(list_product)

    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf= path_wkhtmltopdf)
    rendered = render_template("pdf_template.html", products = list_buyer_products, user= user, buyer = buyer)
    pdf = pdfkit.from_string(rendered, options= {"enable-local-file-access": ""},configuration = config)
    response = make_response(pdf)
    response.headers["Content-Type"] = 'application/pdf'
    response.headers["Content-Disposition"] = 'attachment; filename=output.pdf'
    flash("تم الاستخراج بنجاح", "success")
    return response

# User Routes

def current_user_is_admin(func):
    def checkit():
        try:
            user = User.query.filter_by(id = current_user.id).first()
        except:
            flash("انت لم تسجل بعد", "warning")
            return redirect(url_for("login"))
        else:
            if user:
                if user.IsAdmin():
                    return func()
                else:
                    flash("انت لست مسؤل", "warning")
                    return redirect(url_for("login"))
            else:
                flash("انت لم تسجل بعد", "warning")
                return redirect(url_for("login"))
    return checkit


@app.route("/login", methods = ["post", "get"])
def login():
    loginform = LoginForm()
    if loginform.validate_on_submit():
        user = User.query.filter_by(name = loginform.username.data).first()
        if user and by.check_password_hash(user.password, loginform.password.data):
            login_user(user, remember= loginform.remember_me.data)
            next_page = request.args.get('next')
            n = Notification(notification_name=f"تم تسجيل دخول {current_user.name}",user_id=current_user.id)
            db.session.add(n)
            db.session.commit()
            flash(f"تم تسجيل دخول {current_user.name}", "info")
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for("home"))
        else:
            flash("برجاء ادخال بيانات صحيحة", "danger")
    return render_template("login_page.html", form_login= loginform, title="Login", page_title = "")


@app.route("/signup", methods = ["post", "get"], endpoint='signup')
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
        return redirect(url_for("home"))
    else:
        return render_template("register.html", form = register_form, title = "Registration")

@app.route("/logout", endpoint= "logout")
def logout():
    n = Notification(notification_name=f"تم تسجيل خروج {current_user.name}", user_id=current_user.id)
    db.session.add(n)
    db.session.commit()
    logout_user()
    return redirect(url_for("login"))

@app.route("/change_password", methods = ["POST", "GET"], endpoint= "change_password")
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
    return render_template("change_password_user.html", form = form, page_title = "")

@app.route("/change_user_information", methods = ["POST", "GET"], endpoint= "change_user_information")
@current_user_is_admin
def change_user_information():
    form = ChangeUserInformationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name = form.username_select.data).first()
        if user.admin and user != current_user:
            flash("هذا المستخدم مسؤل لا يمكنك تغير بيناته", "warning")
            return redirect(url_for("user_display"))
        else:
            user.name = form.username.data
            user.phone_num = form.phone_num.data
            user.salary = form.salary.data
            user.admin = form.admin.data
            n = Notification(notification_name=f"تم تغير بيانات المستخدم {user.name} بواسطة {current_user.name}", user_id=current_user.id)
            db.session.add(n)
            db.session.commit()
            flash("تم التغير بنجاح", "success")
            return redirect(url_for("home"))
    return render_template("change_user_information_by_admin.html", form = form)


@app.route("/admin_panel", methods = ["POST", "GET"], endpoint= "admin_panel")
@current_user_is_admin
def admin_panel():
    return render_template("admin_panel.html", page_title = "صفحة الادارة و التحكم")

@app.route("/user_display", endpoint= "user_display")
@current_user_is_admin
def user_display():
    users = User.query.all()
    list_of_users = []
    for i in range(users[-1].id):
        list_user = [users[i].name, users[i].admin, users[i].salary, users[i].phone_num, i+1, users[i].id]
        list_of_users.append(list_user)
    return render_template("user_display.html", users = list_of_users, length= len(list_of_users), page_title = "عرض المستخدمين")

@app.route("/buyers_display", endpoint="buyers_display")
@current_user_is_admin
def buyers_display():
    buyers = Buyer.query.all()
    list_of_buyers = []
    for i in range(buyers[-1].id):
        user = User.query.filter_by(id = buyers[i].user_created_buyer_id).first()
        list_buyers = [buyers[i].name, buyers[i].phone_num, buyers[i].discount, i+1, user, buyers[i].id, buyers[i].money_on_him, buyers[i].money_he_pay, len(buyers[i].goods) ]
        list_of_buyers.append(list_buyers)
    return render_template("buyers_display.html", buyers = list_of_buyers, page_title = "عرض المشتريين")

@app.route("/user/<int:user_id>", endpoint="user_info", methods = ["POST", "GET"])
def user_info(user_id):
    user_data = User.query.get_or_404(user_id)
    if user_data:
        if user_data.admin and user_data != current_user:
            flash("هذا المستخدم مسؤل لا يمكنك تغير بيناته", "warning")
            return redirect(url_for("user_display"))
        else:
            form = ChangeSpecificUserInformationForm()
            try:
                user = User.query.filter_by(id=current_user.id).first()
            except:
                flash("انت لم تسجل بعد", "warning")
                return redirect(url_for("login"))
            else:
                if user:
                    if user.IsAdmin():
                        if form.validate_on_submit():
                            user_data.salary = form.salary.data
                            user_data.name = form.username.data
                            user_data.admin = form.admin.data
                            user_data.phone_num = form.phone_num.data
                            db.session.commit()
                            flash("نم تغير بيانات المستخدم بنجاح", "success")
                            return redirect(url_for("user_display"))
                        return render_template("changespecificuserinformation.html", user= user_data, form = form, page_title = "صفحة المستخدم")
                    else:
                        flash("انت لست مسؤل", "warning")
                        return redirect(url_for("login"))
                else:
                    flash("انت لم تسجل بعد", "warning")
                    return redirect(url_for("login"))

@app.route("/sales_of_today", endpoint="today_sales", methods = ["GET", "POST"])
@current_user_is_admin
def today_sales():
    products = Commodity.query.all()
    list_of_products = []
    counter = 0
    for i in range(products[-1].id):
        buyer = Buyer.query.filter_by(id = products[i].buyer_id).first()
        user = User.query.filter_by(id = products[i].user_created_good_id).first()
        if products[i].date.day == datetime.now().day and products[i].date.month == datetime.now().month and products[i].date.year == datetime.now().year:
            counter += 1
            products_list = [products[i].name, products[i].description, products[i].quantity, products[i].price, counter, products[i].pay_quantity, products[i].date, buyer, user, products[i].id]
            list_of_products.append(products_list)
    return render_template("Today_sales.html", products = list_of_products, page_title = "مبيعات اليوم")

@app.route("/buyer/<int:buyer_id>", endpoint="buyer_edit", methods = ["POST", "GET"])
def buyer_edit(buyer_id):
    buyer_data = Buyer.query.get_or_404(buyer_id)
    if buyer_data:
        form = BuyerEditionForm()
        try:
            user = User.query.filter_by(id=current_user.id).first()
        except:
            flash("انت لم تسجل بعد", "warning")
            return redirect(url_for("login"))
        else:
            # user_data = User.query.filter_by(id = buyer_data.user_created_buyer_id).first()
            if user:
                if user.IsAdmin():
                    if form.validate_on_submit():
                        db.session.commit()
                        flash("نم تغير بيانات المشتري بنجاح", "success")
                        if user.IsAdmin():
                            return redirect(url_for("buyers_display"))
                        else:
                            return redirect(url_for("home"))
                return render_template("buyer_edit.html", form = form, buyer = buyer_data, user = user, page_title ="عرض المشتري")
            else:
                return redirect("home")

@app.route("/get_buyer_name", methods = ["POST", "GET"], endpoint= "get_buyer_name")
def get_buyer_name():
    form = GetBuyerNameForm()
    if form.validate_on_submit():
        buyer = Buyer.query.filter_by(name = form.name_buyer.data).first()
        return redirect(url_for("buyer_edit", buyer_id= buyer.id))
    return render_template("get_buyer_name.html", form = form)


@app.route("/product_edit_<int:product_id>", endpoint="product_edit_admin", methods = ["POST", "GET"])
def product_edit_admin(product_id):
    try:
        user = User.query.filter_by(id=current_user.id).first()
    except:
        flash("انت لم تسجل بعد", "warning")
        return redirect(url_for("login"))
    else:
        if user:
            if user.IsAdmin():
                product = Commodity.query.get_or_404(product_id)
                form = ProductEditForm()
                buyer = Buyer.query.filter_by(id = product.buyer_id).first()
                if form.validate_on_submit():
                    return redirect(url_for("goods_display"))
                form.name_buyer.data = buyer.name
                return render_template("product_edit_admin.html", form = form, product = product)
            else:
                flash("انت لست مسؤل", "warning")
                return redirect(url_for("login"))
        else:
            flash("انت لم تسجل بعد", "warning")
            return redirect(url_for("login"))

@app.route("/same_product_<int:product_id>",  endpoint="all_this_product")
def all_this_product(product_id):
    product = Commodity.query.get_or_404(product_id)
    buyers = Buyer.query.all()
    user = User.query.filter_by(id = product.user_created_good_id).first()
    list_products = []
    counter = 0
    for buyer in buyers:
        for i in buyer.goods:
            if i.name == product.name:
                counter += 1
                product_user_list = [counter, i, buyer, user]
                list_products.append(product_user_list)
    return render_template("all_this_product.html", page_title=f"المنتجات المباعة من {product.name}", products = list_products)

@app.route("/choose_date", methods = ["POST", "GET"], endpoint= "choose_date")
@current_user_is_admin
def choose_date():
    form = AllSalesInDate()
    if form.validate_on_submit():
        return redirect(url_for("sales_one_day", day= form.date.data.day, month= form.date.data.month, year= form.date.data.year))
    return render_template("select_date.html", form = form, page_title ="عرض مبيعات تاريخ محدد")


@app.route("/sales_one_day/<int:day>/<int:month>/<int:year>", endpoint= "sales_one_day")
def sales_one_day(day, month, year):
    try:
        user = User.query.filter_by(id=current_user.id).first()
    except:
        flash("انت لم تسجل بعد", "warning")
        return redirect(url_for("login"))
    else:
        if user:
            if user.IsAdmin():
                products = Commodity.query.all()
                list_of_products = []
                counter = 0
                for product in products:
                    if product.date.day == day and product.date.month == month and product.date.year == year:
                        user = User.query.filter_by(id = product.user_created_good_id).first()
                        buyer = Buyer.query.filter_by(id = product.buyer_id).first()
                        counter += 1
                        products_list = [counter, product, buyer, user]
                        list_of_products.append(products_list)
                return render_template("sales_one_day.html", products = list_of_products)
            else:
                flash("انت لست مسؤل", "warning")
                return redirect(url_for("login"))
        else:
            flash("انت لم تسجل بعد", "warning")
            return redirect(url_for("login"))


