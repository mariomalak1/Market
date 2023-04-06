from flask import render_template, redirect, url_for, flash, Blueprint, request
from flask_sqlalchemy import Pagination
from werkzeug.routing import BaseConverter
from Market import db, app
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
        db.session.add(commodity)

        # modify money of buyer of product
        total = commodity.quantity * commodity.price
        buyer.money_on_him += total - ( (total / 100 ) * buyer.discount ) - commodity.pay_quantity

        n = Notification(notification_name=f"""        تم انشاء منتج جديد
        اسم المنتج : {commodity.name}
        للمشتري : {buyer.name}
        سعره : {commodity.price}
        الكمية بالكيلو : {commodity.quantity}
        المشتري دفع : {commodity.pay_quantity}
        الاجمالي : {commodity.price * commodity.quantity}
        منشيء المعاملة : {current_user.name}""", user_id=current_user.id)
        db.session.add(n)

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
    list_of_products = []
    counter = 0
    products = Commodity.query.all()
    for product_ in products:
        if product_.date.day == datetime.now().day and product_.date.month == datetime.now().month and product_.date.year == datetime.now().year:
            buyer = Buyer.query.filter_by(id = product_.buyer_id).first()
            user = User.query.filter_by(id = product_.user_created_good_id).first()
            counter += 1
            products_list = [product_.name, product_.description, product_.quantity, product_.price, counter, product_.pay_quantity, product_.date, buyer, user, product_.id]
            list_of_products.append(products_list)
    per_page = 15
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * per_page
    end = start + per_page
    items = list_of_products[start:end]
    pagination = Pagination(None, page, per_page, len(list_of_products), items)
    n = Notification(notification_name=f"""تم دخول المستخدم {current_user.name} الي صفحة مبيعات اليوم""", user_id=current_user.id)
    db.session.add(n)
    return render_template("product_templates/Today_sales.html", products = pagination, page_title ="مبيعات اليوم")


@product.route("/product_edit_<int:product_id>/<place>", endpoint="product_edit", methods = ["POST", "GET"])
def product_edit(product_id, place):
    product_ = Commodity.query.get_or_404(product_id)
    buyer = Buyer.query.filter_by(id = product_.buyer_id).first()
    date_product = datetime(year = product_.date.year, month= product_.date.month, day= product_.date.day)
    if product_:
        try:
            user = User.query.filter_by(id=current_user.id).first()
        except:
            n = Notification(notification_name=f"""شخص ما غير مسجل علي النظام حاول الدخول للصفحات المخصصة للمسؤل فقد و لكن تم حذره من قبل النظام 
                اذا تكرر الامر برجاء مكالمة الصيانة للتبليغ عن الامر و محاولة التعامل معه""", user_id=1)
            db.session.add(n)
            db.session.commit()
            flash("انت لم تسجل بعد", "warning")
            return redirect(url_for("user.login"))
        else:
            if user:
                form = ProductAdminEditForm()
                if form.date.data:
                    pass
                else:
                    form.date.data = date_product
                if user.IsAdmin():
                    if form.validate_on_submit():

                        n = Notification(notification_name=f"""تم تغير منتج
                        اسم المنتج :  {product_.name} اصبح -> {form.name.data}
                        اسم المشتري :  {form.name_buyer.data}
                        سعره :  {product_.price} اصبح -> {form.price.data}
                        الكمية بالكيلو :  {product_.quantity} اصبح -> {form.quantity.data}
                        الفلوس اللي دفعها :  {product_.pay_quantity} اصبح -> {form.pay_quantity.data}
                        وصف المعاملة :  {product_.description} اصبح -> {form.description.data}
                        عن طريق المستخدم المسؤل :  {user.name}
                        لاحظ ان التغير في المنتج سوف يخصم الحساب القديم من المشتري الخاص بيه و سوف يتم وضع الحساب الجديد للمشتري الخاص بيه""", user_id=current_user.id)
                        db.session.add(n)

                        # delete old money transactions and, but the new one
                        total = product_.quantity * product_.price
                        buyer.money_on_him -= total
                        buyer.money_on_him += ((total / 100) * buyer.discount) + product_.pay_quantity
                        # add the new transaction
                        total = form.quantity.data * form.price.data
                        buyer.money_on_him += total - ((total / 100) * buyer.discount) - form.pay_quantity.data

                        product_.date = form.date.data
                        product_.name = form.name.data
                        buyer_2 = Buyer.query.filter_by(name = form.name_buyer.data).first()
                        product_.buyer_id = buyer_2.id
                        product_.price = form.price.data
                        product_.quantity = form.quantity.data
                        product_.description = form.description.data
                        product_.pay_quantity = form.pay_quantity.data

                        db.session.commit()
                        flash("تم التعديل بنجاح", "success")
                        if place == "today_sales":
                            return redirect(url_for("product.today_sales"))
                        else:
                            return redirect(url_for("main.home"))
                else:
                    if form.validate_on_submit():

                        n = Notification(notification_name=f"""  تم تغير منتج 
                        اسم المنتج :  {product_.name} اصبح -> {form.name.data}
                        اسم المشتري :  {product_.name} اصبح -> {form.name_buyer.data}
                        سعره :  {product_.price} اصبح -> {form.price.data}
                        الكمية بالكيلو :  {product_.quantity} اصبح -> {form.quantity.data}
                        الفلوس اللي دفعها :  {product_.pay_quantity} اصبح -> {form.pay_quantity.data}
                        وصف المعاملة :  {product_.description} اصبح -> {form.description.data}
                        عن طريق المستخدم :  {user.name}
                        لاحظ ان التغير في المنتج سوف يخصم الحساب القديم من المشتري الخاص بيه و سوف يتم وضع الحساب الجديد للمشتري الخاص بيه""", user_id=current_user.id)
                        db.session.add(n)

                        # delete old money transactions and, but the new one
                        total = product_.quantity * product_.price
                        buyer.money_on_him -= total
                        buyer.money_on_him += ((total / 100) * buyer.discount) + product_.pay_quantity
                        # add the new transaction
                        total = form.quantity.data * form.price.data
                        buyer.money_on_him += total - ((total / 100) * buyer.discount) - form.pay_quantity.data

                        product_.date = form.date.data
                        product_.name = form.name.data
                        buyer_2 = Buyer.query.filter_by(name = form.name_buyer.data).first()
                        product_.buyer_id = buyer_2.id
                        product_.price = form.price.data
                        product_.quantity = form.quantity.data
                        product_.description = form.description.data
                        product_.pay_quantity = form.pay_quantity.data

                        db.session.commit()
                        flash("تم التعديل بنجاح", "success")
                        return redirect(url_for("main.home"))
                return render_template("product_templates/product_edit.html", form=form, product= product_, user = user, buyer = buyer, date_product = date_product)
            else:
                n = Notification(notification_name=f"""شخص ما غير مسجل علي النظام حاول الدخول للصفحات المخصصة للمسؤل فقد و لكن تم حذره من قبل النظام 
                    اذا تكرر الامر برجاء مكالمة الصيانة للتبليغ عن الامر و محاولة التعامل معه""", user_id=1)
                db.session.add(n)
                db.session.commit()
                flash("انت لم تسجل بعد", "warning")
                return redirect(url_for("user.login"))


@product.route("/same_product_<int:product_id>",  endpoint="all_this_product")
def all_this_product(product_id):
    product_ = Commodity.query.get_or_404(product_id)
    if product_:
        try:
            user = User.query.filter_by(id=current_user.id).first()
        except:
            n = Notification(notification_name=f"""شخص ما غير مسجل علي النظام حاول الدخول للصفحات المخصصة للمسؤل فقد و لكن تم حذره من قبل النظام 
                اذا تكرر الامر برجاء مكالمة الصيانة للتبليغ عن الامر و محاولة التعامل معه""", user_id=1)
            db.session.add(n)
            db.session.commit()
            flash("انت لم تسجل بعد", "warning")
            return redirect(url_for("user.login"))
        else:
            if user:
                if user.IsAdmin():
                    buyers = Buyer.query.all()
                    user = User.query.filter_by(id = product_.user_created_good_id).first()
                    list_products = []
                    counter = 0
                    for buyer in buyers:
                        for i in buyer.goods:
                            if i.name == product_.name:
                                counter += 1
                                product_user_list = [counter, i, buyer, user]
                                list_products.append(product_user_list)
                    per_page = 15
                    page = request.args.get("page", 1, type=int)
                    start = (page - 1) * per_page
                    end = start + per_page
                    items = list_products[start:end]
                    pagination = Pagination(None, page, per_page, len(list_products), items)
                    n = Notification(notification_name=f"""تم عرض كل المنتجات المباعة من قبل المستخدم المسؤل : {current_user.name}""", user_id=current_user.id)
                    db.session.add(n)
                    db.session.commit()
                    return render_template("product_templates/all_this_product.html", page_title=f"المنتجات المباعة من {product_.name}", products = pagination)
                else:
                    n = Notification(
                        notification_name=f"""لقد حاول المستخدم {user.name} الدخول الي الصفحات المخصصة للمسؤل فقد و النظام منعه""",
                        user_id=current_user.id)
                    db.session.add(n)
                    db.session.commit()
                    flash("انت لست مسؤل", "warning")
                    return redirect(url_for("user.login"))
            else:
                n = Notification(notification_name=f"""شخص ما غير مسجل علي النظام حاول الدخول للصفحات المخصصة للمسؤل فقد و لكن تم حذره من قبل النظام 
                    اذا تكرر الامر برجاء مكالمة الصيانة للتبليغ عن الامر و محاولة التعامل معه""", user_id=1)
                db.session.add(n)
                db.session.commit()
                flash("انت لم تسجل بعد", "warning")
                return redirect(url_for("user.login"))

@product.route("/sales_one_day/<int:day>/<int:month>/<int:year>", endpoint= "sales_one_day")
def sales_one_day(day, month, year):
    try:
        user = User.query.filter_by(id=current_user.id).first()
    except:
        n = Notification(notification_name=f"""شخص ما غير مسجل علي النظام حاول الدخول للصفحات المخصصة للمسؤل فقد و لكن تم حذره من قبل النظام 
            اذا تكرر الامر برجاء مكالمة الصيانة للتبليغ عن الامر و محاولة التعامل معه""", user_id=1)
        db.session.add(n)
        db.session.commit()
        flash("انت لم تسجل بعد", "warning")
        return redirect(url_for("user.login"))
    else:
        if user:
            if user.IsAdmin():
                products = Commodity.query.all()
                list_of_products = []
                counter = 0
                for product_ in products:
                    if product_.date.day == day and product_.date.month == month and product_.date.year == year:
                        user = User.query.filter_by(id = product_.user_created_good_id).first()
                        buyer = Buyer.query.filter_by(id = product_.buyer_id).first()
                        counter += 1
                        products_list = [counter, product_, buyer, user]
                        list_of_products.append(products_list)
                per_page = 15
                page = request.args.get("page", 1, type=int)
                start = (page - 1) * per_page
                end = start + per_page
                items = list_of_products[start:end]
                pagination = Pagination(None, page, per_page, len(list_of_products), items)
                n = Notification(notification_name=f"""تم عرض كل المنتجات المباعة اليوم من قبل المستخدم المسؤل : {current_user.name}""",
                    user_id=current_user.id)
                db.session.add(n)
                return render_template("product_templates/sales_one_day.html", products = pagination, day = day, month = month, year = year)
            else:
                n = Notification(
                    notification_name=f"""لقد حاول المستخدم {user.name} الدخول الي الصفحات المخصصة للمسؤل فقد و النظام منعه""",
                    user_id=current_user.id)
                db.session.add(n)
                db.session.commit()
                flash("انت لست مسؤل", "warning")
                return redirect(url_for("user.login"))
        else:
            n = Notification(notification_name=f"""شخص ما غير مسجل علي النظام حاول الدخول للصفحات المخصصة للمسؤل فقد و لكن تم حذره من قبل النظام 
                اذا تكرر الامر برجاء مكالمة الصيانة للتبليغ عن الامر و محاولة التعامل معه""", user_id=1)
            db.session.add(n)
            db.session.commit()
            flash("انت لم تسجل بعد", "warning")
            return redirect(url_for("user.login"))

class IntListConverter(BaseConverter):
    """Match ints separated with ';'."""

    # at least one int, separated by ;, with optional trailing ;
    regex = r'\d+(?:;\d+)*;?'

    # this is used to parse the url and pass the list to the view function
    def to_python(self, value):
        return [int(x) - 789 for x in value.split(';')]

    # this is used when building an url with url_for
    def to_url(self, value):
        return ';'.join(str(x + 789) for x in value)

app.url_map.converters['int_list'] = IntListConverter

@product.route("/find_product", methods = ["POST", "GET"])
@login_required
def find_product():
    form = FindProductForm()
    list_of_buyers = Buyer.query.all()
    list_names = []
    for buyer_ in list_of_buyers:
        list_names.append(buyer_.name)

    if form.validate_on_submit():
        buyer = Buyer.query.filter_by(name=form.buyer_name.data).first()
        list_of_ids = []
        if "submit_1" in request.form:
            if request.form["submit_1"] == 'بحث في كل التواريخ':
                if current_user.IsAdmin():
                    for product_name in buyer.goods:
                        if product_name.name == form.product_name.data:
                            list_of_ids.append(product_name.id)
                else:
                    for product_name in buyer.goods:
                        if product_name.name == form.product_name.data and product_name.user_created_good_id == current_user.id:
                            list_of_ids.append(product_name.id)
                if not list_of_ids:
                    n = Notification(
                        notification_name=f"""تم بحث المستخدم {current_user.name} عن {form.product_name.data} للمشتري {form.buyer_name.data}و لكن لم يجده""",
                        user_id=current_user.id)
                    db.session.add(n)
                    db.session.commit()
                    flash("هذا المنتج لا يوجد لدي هذا المشتري", "warning")
                    return redirect(url_for("product.find_product"))
                else:
                    n = Notification(
                        notification_name=f"""تم بحث المستخدم {current_user.name} عن {form.product_name.data} للمشتري {form.buyer_name.data}""",
                        user_id=current_user.id)
                    db.session.add(n)
                    db.session.commit()
                    return redirect(url_for("product.display_all_products", buyer_id= buyer.id, list_ids = list_of_ids))
        elif "submit" in request.form:
            if request.form["submit"] == 'بحث':
                list_of_ids = []
                date_from = datetime(day=form.date_from.data.day, month=form.date_from.data.month,
                                     year=form.date_from.data.year)
                date_to = datetime(day=form.date_to.data.day, month=form.date_to.data.month,
                                   year=form.date_to.data.year)
                if current_user.IsAdmin():
                    for product_name in buyer.goods:
                        if product_name.name == form.product_name.data and date_from <= product_name.date <= date_to:
                            list_of_ids.append(product_name.id)

                else:
                    for product_name in buyer.goods:
                        if product_name.name == form.product_name.data and product_name.user_created_good_id == current_user.id and date_from <= product_name.date <= date_to:
                            list_of_ids.append(product_name.id)
                if not list_of_ids:
                    n = Notification(
                        notification_name=f"""تم بحث المستخدم {current_user.name} عن {form.product_name.data} للمشتري {form.buyer_name.data}و لكن لم يجده""",
                        user_id=current_user.id)
                    db.session.add(n)
                    db.session.commit()

                    flash("هذا المنتج لا يوجد لدي هذا المشتري في هذه الفترة", "warning")
                    return redirect(url_for("product.find_product"))
                else:
                    n = Notification(
                        notification_name=f"""تم بحث المستخدم {current_user.name} عن {form.product_name.data} للمشتري {form.buyer_name.data}""",
                        user_id=current_user.id)
                    db.session.add(n)
                    db.session.commit()
                    return redirect(url_for("product.display_all_products", buyer_id= buyer.id, list_ids = list_of_ids))
    return render_template("product_templates/find_product.html", form = form, list_names = list_names)


@product.route("/display_all_products_<int:buyer_id>/<int_list:list_ids>")
@login_required
def display_all_products(buyer_id, list_ids):
    buyer = Buyer.query.get_or_404(buyer_id)
    list_of_products = []
    counter = 0
    for product_id in list_ids:
        counter += 1
        product_ = Commodity.query.get_or_404(product_id)
        user = User.query.filter_by(id = product_.user_created_good_id).first()
        product_list = [counter, product_, buyer, user]
        list_of_products.append(product_list)
    n = Notification(notification_name=f"""{current_user.name} للمشتري  {buyer.name} تم عرض كل المنتجات التي سجلها المستخدم """, user_id=current_user.id)
    db.session.add(n)

    return render_template("product_templates/display_all_products.html", products = list_of_products, buyer = buyer)

@product.route("/delete_product_<int:product_id>_<string:place>", endpoint= "delete_product")
def delete_product(product_id, place):
    product_ = Commodity.query.get_or_404(product_id)
    if product_:
        try:
            user = User.query.filter_by(id=current_user.id).first()
        except:
            n = Notification(notification_name=f"""شخص ما غير مسجل علي النظام حاول الدخول للصفحات المخصصة للمسؤل فقد و لكن تم حذره من قبل النظام 
                اذا تكرر الامر برجاء مكالمة الصيانة للتبليغ عن الامر و محاولة التعامل معه""", user_id=1)
            db.session.add(n)
            db.session.commit()
            flash("انت لم تسجل بعد", "warning")
            return redirect(url_for("user.login"))
        else:
            if user:
                if user.IsAdmin():
                    user_product = User.query.filter_by(id = product_.user_created_good_id).first()
                    buyer = Buyer.query.filter_by(id = product_.buyer_id).first()

                    total = product_.quantity * product_.price
                    money_of_buyer = buyer.money_on_him
                    buyer.money_on_him -= total + ((total / 100) * buyer.discount) + product_.pay_quantity

                    n = Notification(notification_name=f"""تم ازالة بيانات منتج
                    اسم المنتج : {product_.name}
                    اسم المشتري : {buyer.name}
                    وصفه : {product_.description}
                    عدده : {product_.quantity} 
                    سعره : {product_.price}
                    كان مدفوع فيه من قبل المشتري : {product_.pay_quantity}
                    تاريخ المعاملة : {product_.date.strftime("%Y-%m-%d")} 
                    اسم المستخدم الذي ازاله: {current_user.name}
                    حساب المشتري الذي اشتري المنتج اصبح : {buyer.money_on_him} بعد ان كان : {money_of_buyer}:
                     منشيء المشتري :{user_product.name}""", user_id=current_user.id)

                    db.session.add(n)
                    db.session.delete(product_)
                    db.session.commit()
                    flash("تم ازالة المنتج بنجاح", "success")
                    return redirect(url_for(place))
                else:
                    n = Notification(
                        notification_name=f"""لقد حاول المستخدم {user.name} الدخول الي الصفحات المخصصة للمسؤل فقد و النظام منعه""",
                        user_id=current_user.id)
                    db.session.add(n)
                    db.session.commit()
                    flash("انت لست مسؤل", "warning")
                    return redirect(url_for("user.login"))
            else:
                n = Notification(notification_name=f"""شخص ما غير مسجل علي النظام حاول الدخول للصفحات المخصصة للمسؤل فقد و لكن تم حذره من قبل النظام 
                    اذا تكرر الامر برجاء مكالمة الصيانة للتبليغ عن الامر و محاولة التعامل معه""", user_id=1)
                db.session.add(n)
                db.session.commit()
                flash("انت لم تسجل بعد", "warning")
                return redirect(url_for("user.login"))