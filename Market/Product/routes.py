from flask import render_template, redirect, url_for, flash, Blueprint
from Market import db
from Market.Product.forms import *
from Market.User.models import User
from Market.Buyer.models import Buyer
from Market.Product.models import Commodity
from Market.Main.models import Notification
from Market.User.routes import current_user_is_admin
from flask_login import current_user, login_required

product = Blueprint("product", __name__)

@product.route("/add_products", methods = ["POST", "GET"])
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
        return redirect(url_for("product.add_products"))
    list_of_users = Buyer.query.all()
    list_names = []
    for user in list_of_users:
        list_names.append(user.name)
    return render_template("product_templates/add_products.html", form = form, list_names = list_names, title ="Add products", page_title ="تسجيل منتج")

@product.route("/sales_of_today", endpoint="today_sales", methods = ["GET", "POST"])
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
    return render_template("product_templates/Today_sales.html", products = list_of_products, page_title ="مبيعات اليوم")


@product.route("/product_edit_<int:product_id>", endpoint="product_edit_admin", methods = ["POST", "GET"])
def product_edit_admin(product_id):
    try:
        user = User.query.filter_by(id=current_user.id).first()
    except:
        flash("انت لم تسجل بعد", "warning")
        return redirect(url_for("user.login"))
    else:
        if user:
            if user.IsAdmin():
                product = Commodity.query.get_or_404(product_id)
                form = ProductEditForm()
                buyer = Buyer.query.filter_by(id = product.buyer_id).first()
                if form.validate_on_submit():
                    return redirect(url_for("product.goods_display"))
                form.name_buyer.data = buyer.name
                return render_template("product_templates/product_edit_admin.html", form = form, product = product)
            else:
                flash("انت لست مسؤل", "warning")
                return redirect(url_for("user.login"))
        else:
            flash("انت لم تسجل بعد", "warning")
            return redirect(url_for("user.login"))

@product.route("/same_product_<int:product_id>",  endpoint="all_this_product")
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
    return render_template("product_templates/all_this_product.html", page_title=f"المنتجات المباعة من {product.name}", products = list_products)


@product.route("/sales_one_day/<int:day>/<int:month>/<int:year>", endpoint= "sales_one_day")
def sales_one_day(day, month, year):
    try:
        user = User.query.filter_by(id=current_user.id).first()
    except:
        flash("انت لم تسجل بعد", "warning")
        return redirect(url_for("user.login"))
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
                return render_template("product_templates/sales_one_day.html", products = list_of_products)
            else:
                flash("انت لست مسؤل", "warning")
                return redirect(url_for("user.login"))
        else:
            flash("انت لم تسجل بعد", "warning")
            return redirect(url_for("user.login"))