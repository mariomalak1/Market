from Market import db
from flask import render_template, redirect, url_for, flash, make_response, Blueprint, request
from Market.Buyer.forms import *
from Market.Buyer.models import Buyer
from Market.User.models import User
from Market.Main.models import Notification
from Market.Product.models import Commodity
from flask_login import current_user, login_required
from Market.User.routes import current_user_is_admin
import pdfkit
import io
from PyPDF2 import PdfReader, PdfWriter, PdfMerger

# Buyer routes is here

buyer = Blueprint("buyer", __name__)

@buyer.route("/make_buyer", methods = ["POST", "GET"])
@login_required
def make_buyer():
    form = MakeBuyerForm()
    if form.validate_on_submit():
        buyer_ = Buyer(name = form.name.data, description = form.description.data,
                      phone_num = form.phone_num.data,
                      money_on_him = form.money_on_him.data,
                      last_collection_money = form.last_collection_money.data,
                      discount = form.discount.data, user_created_buyer_id = current_user.id)

        n = Notification(notification_name=f"""تم اضافة مشتري جديد 
        اسم : {buyer_.name}
        رقم تليفونه : {buyer_.phone_num}
        وصفه : {buyer_.description}
        خصم :{buyer_.discount} 
        اسم المستخدم الذي اضافه: {current_user.name}
         فلوس عليه : {buyer_.money_on_him}
         اخر دفعة : {buyer_.last_collection_money}
        """, user_id=current_user.id)
        db.session.add(buyer_)
        db.session.add(n)
        db.session.commit()
        flash("تم اضافة مشتري", "success")
        return redirect(url_for("buyer.make_buyer"))
    return render_template("buyer_templates/make_buyer.html", title ="make buyer", form = form, page_title ="تسجيل مشتري")


@buyer.route("/Account_statement", methods = ["POST", "GET"], endpoint= "account_statement")
@login_required
def account_statement():
    form = AccountStatementForm()
    if form.validate_on_submit():
        buyer_ = Buyer.query.filter_by(name = form.buyer_name.data).first()
        date_from_day = form.date_from.data.day
        date_from_month = form.date_from.data.month
        date_from_year = form.date_from.data.year
        date_to_day = form.date_to.data.day
        date_to_month = form.date_to.data.month
        date_to_year = form.date_to.data.year
        return redirect(url_for("buyer.account_statement_response", buyer_id= buyer_.id,
        date_from_day = date_from_day, date_from_month = date_from_month, date_from_year = date_from_year,
        date_to_day = date_to_day, date_to_month = date_to_month, date_to_year = date_to_year))
    list_of_users = Buyer.query.all()
    list_names = []
    for user in list_of_users:
        list_names.append(user.name)
    return render_template("buyer_templates/account_statement.html", list_names = list_names, form = form, page_title ="كشف حساب")

#  to loop on products and get it in the pdf correctly
def list_buyer_some_products(list_buyer_products, num_pages):
    if num_pages == 1:
        return list_buyer_products, list_buyer_products
    else:
        list_buyer_products_new = []
        counter = -1
        while True:
            if len(list_buyer_products_new) == 13 or list_buyer_products == []:
                return list_buyer_products_new, list_buyer_products
            list_buyer_products_new.append(list_buyer_products[counter])
            list_buyer_products.pop()

def make_pdf(list_buyer_products, user, buyer_, date_from, date_to, total_product_money, num_pages, perivous_money_history, page_num, cond =""):
    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    if page_num == 1:
        if cond:
            page_num = -1
        rendered = render_template("buyer_templates/invoice.html", products=list_buyer_products, user=user, buyer=buyer_,
            date_from=date_from, date_to=date_to, date_today=datetime.now(),
            total_products_money=total_product_money, perivous_money_history=perivous_money_history,
            num_pages=num_pages, num_page=page_num, num_products=len(list_buyer_products))
    else:
        if cond:
            page_num = -1
        rendered = render_template("buyer_templates/invoice_more_than_15.html", products=list_buyer_products, user=user, buyer=buyer_,
            date_from=date_from, date_to=date_to, date_today=datetime.now(),
            total_products_money=total_product_money, perivous_money_history=perivous_money_history,
            num_pages=num_pages, num_page=page_num, num_products=len(list_buyer_products))
    options = {
        'dpi': 365,
        'page-size': 'A4',
        'margin-top': '0in',
        'margin-right': '0in',
        'margin-bottom': '0in',
        'margin-left': '0in',
        'encoding': "UTF-8",
        'custom-header': [
            ('Accept-Encoding', 'gzip')
        ],
        'no-outline': None,
        "enable-local-file-access": "",
    }
    pdf = pdfkit.from_string(rendered, options=options, configuration=config)
    return pdf


@buyer.route("/Account_statement_response/<int:buyer_id>/<int:date_from_day>/<int:date_from_month>/"
           "<int:date_from_year>/<int:date_to_day>/<int:date_to_month>/<int:date_to_year>",
           methods = ["POST", "GET"], endpoint="account_statement_response")
@login_required
def account_statement_response(buyer_id, date_from_day, date_from_month, date_from_year, date_to_day, date_to_month, date_to_year):
    date_from = datetime(date_from_year, date_from_month, date_from_day)
    date_to = datetime(date_to_year, date_to_month, date_to_day)
    buyer_ = Buyer.query.get_or_404(buyer_id)
    user = User.query.filter_by(id = buyer_.user_created_buyer_id).first()
    list_buyer_products = []
    counter = 0
    total_product_money = 0
    perivous_money_history = 0

    # to loop on the buyers products and get all products in this period of time
    for product in buyer_.goods:
        total = product.quantity * product.price
        if date_from <= product.date <= date_to:

            total_product_money += total - ((total / 100) * buyer_.discount) - product.pay_quantity
            counter += 1
            list_product = [counter, product, buyer_, user]
            list_buyer_products.append(list_product)

        else:
            perivous_money_history += total - ((total / 100) * buyer_.discount) - product.pay_quantity

    # to get number of pages
    num_pages = 0
    products_length = len(list_buyer_products)
    if products_length % 13 == 0:
        num_pages = products_length / 13
    else:
        while products_length > 0:
            products_length -= 13
            num_pages += 1

    # list to get all pdf pages in it
    list_pages_of_pdf = []

    if num_pages >= 1:
        counter_page = 0
        cond = ""
        for i in range(num_pages):
            counter_page += 1
            if counter_page == num_pages:
                cond = "last"
            list_buyer_products_new, list_buyer_products = list_buyer_some_products(list_buyer_products, num_pages)
            pdf = make_pdf(list_buyer_products_new, user, buyer_, date_from, date_to, total_product_money, num_pages, perivous_money_history, i + 1, cond)

            # variable to make pdf bytes as file to edit it
            input_stream_bytes = io.BytesIO(pdf)
            # to read the pdf file
            reader = PdfReader(input_stream_bytes, 'r')

            # to crop the important part in pdf page
            page = reader.pages[0]
            page.cropbox.lower_left = (0, 215)
            page.cropbox.upper_left = (0, 842)
            page.cropbox.upper_right = (595, 842)
            page.cropbox.lower_right = (595, 215)

            # to write the important part in a variable as file
            writer = PdfWriter()
            writer.add_page(page)
            # variable that the output stream of writer object write in it
            output_pdf_writer = io.BytesIO()

            writer.write(output_pdf_writer)
            output_pdf_writer.seek(0)

            list_pages_of_pdf.append(output_pdf_writer)

    merger = PdfMerger()
    for pdf_page in list_pages_of_pdf:
        merger.append(pdf_page)
    output_pdf_merger = io.BytesIO()

    merger.write(output_pdf_merger)
    output_pdf_merger.seek(0)

    n = Notification(
        notification_name=f"تم عمل كشف حساب ل {buyer_.name} من قبل {current_user.name} من تاريخ {date_from.strftime('%Y-%m_%d')} الي تاريخ {date_to.strftime('%Y-%m-%d')}",
        user_id=current_user.id)
    db.session.add(buyer_)
    db.session.add(n)
    db.session.commit()

    response = make_response(output_pdf_merger)
    response.headers["Content-Type"] = 'application/pdf'
    response.headers["Content-Disposition"] = 'attachment; filename=output.pdf'

    flash("تم الاستخراج بنجاح", "success")

    return response


@buyer.route("/buyers_display", endpoint="buyers_display")
@current_user_is_admin
def buyers_display():
    page = request.args.get("page", 1, type=int)
    buyers = Buyer.query.order_by(Buyer.id.desc()).paginate(page = page, per_page = 10)
    list_of_buyers = []
    counter = ((buyers.page - 1) * buyers.per_page) + 1
    for buyer_ in buyers.items:
        user = User.query.filter_by(id = buyer_.user_created_buyer_id).first()
        list_buyers = [counter, buyer_, user, len(buyer_.goods)]
        list_of_buyers.append(list_buyers)
        counter += 1
    n = Notification(notification_name=f"تم عرض كل المشتريين من قبل {current_user.name}", user_id=current_user.id)
    db.session.add(n)
    db.session.commit()
    return render_template("buyer_templates/buyers_display.html", buyers = list_of_buyers, page_title ="عرض المشتريين", buyers_pagination = buyers)


@buyer.route("/buyer/<int:buyer_id>/<string:place>", endpoint="buyer_edit_admin_user", methods = ["POST", "GET"])
@login_required
def buyer_edit_admin_user(buyer_id, place):
    buyer_data = Buyer.query.get_or_404(buyer_id)
    user_buyer = User.query.filter_by(id = buyer_data.user_created_buyer_id).first()
    form = BuyerEditionAdminForm()
    if buyer_data:
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
                    if form.validate_on_submit():
                        n = Notification(notification_name=f"""تم تغير بيانات المشتري 
                        الاسم : {buyer_data.name} اصبح: {form.name.data}
                        رقم التليفون : {buyer_data.phone_num} اصبح : {form.phone_num.data}
                        وصفه : {buyer_data.description} اصبح : {form.description.data}
                        الخصم : {buyer_data.discount} اصبح : {form.discount.data}
                        عدد منتجاته : {len(buyer_data.goods)}
                        اسم المستخدم المسؤل الذي غير بياناته: {current_user.name}
                        الفلوس اللي عليه اصبحت : {buyer_data.money_on_him} اصبحت : {form.money_on_him.data} 
                        الفلوس اللي دفعها : {buyer_data.last_collection_money} اصبحت : {form.last_collection_money.data}
                         منشيء المشتري : {user_buyer.name}""", user_id=current_user.id)

                        db.session.add(n)

                        buyer_data.money_on_him += buyer_data.last_collection_money

                        buyer_data.name = form.name.data
                        buyer_data.phone_num = form.phone_num.data
                        buyer_data.discount = form.discount.data
                        buyer_data.description = form.description.data
                        buyer_data.money_on_him = form.money_on_him.data
                        buyer_data.last_collection_money = form.last_collection_money.data

                        buyer_data.money_on_him -= buyer_data.last_collection_money

                        db.session.commit()
                        flash("نم تغير بيانات المشتري بنجاح", "success")
                        if place == "buyers_display":
                            return redirect(url_for("buyer.buyers_display"))
                        elif place == "today_sales":
                            return redirect(url_for("product.today_sales"))
                        else:
                            return redirect(url_for("main.home"))
                    list_products_of_buyer = []
                    page = request.args.get("page", 1, type=int)
                    products_buyer = Commodity.query.filter_by(buyer_id = buyer_data.id).order_by(Commodity.date.desc()).paginate(page = page, per_page = 8)
                    counter = ((products_buyer.page - 1) * products_buyer.per_page) + 1
                    for product in products_buyer.items:
                        user_product = User.query.filter_by(id = product.user_created_good_id).first()
                        list_products = [counter, product, user_product]
                        list_products_of_buyer.append(list_products)
                        counter += 1
                    return render_template("buyer_templates/buyer_edit_by_admin.html", form=form, products = list_products_of_buyer, buyer = buyer_data, user = user, user_buyer = user_buyer, page_title="عرض المشتري", products_buyer_pagination = products_buyer)
                else:
                    n = Notification(
                        notification_name=f"""لقد حاول المستخدم {user.name} الدخول الي الصفحات المخصصة للمسؤل فقد و النظام منعه""",
                        user_id=current_user.id)
                    db.session.add(n)
                    db.session.commit()
                    flash("انت لست مسؤل", "warning")
                    return redirect("user.login")
            else:
                n = Notification(notification_name=f"""شخص ما غير مسجل علي النظام حاول الدخول للصفحات المخصصة للمسؤل فقد و لكن تم حذره من قبل النظام 
                    اذا تكرر الامر برجاء مكالمة الصيانة للتبليغ عن الامر و محاولة التعامل معه""", user_id=1)
                db.session.add(n)
                db.session.commit()
                flash("انت لم تسجل بعد", "warning")
                return redirect("user.login")

@buyer.route("/buyer_edit/<int:buyer_id>", endpoint= "buyer_edit", methods = ["POST", "GET"])
@login_required
def buyer_edit(buyer_id):
    buyer_data = Buyer.query.get_or_404(buyer_id)
    form = BuyerEditionForm()
    if buyer_data:
        try:
            user = User.query.filter_by(id=current_user.id).first()
            user_buyer = User.query.filter_by(id=buyer_data.user_created_buyer_id).first()
        except:
            flash("انت لم تسجل بعد", "warning")
            return redirect(url_for("user.login"))
        else:
            if user:
                if form.validate_on_submit():
                    n = Notification(notification_name=f"""تم تغير بيانات المشتري 
                    الاسم : {buyer_data.name}
                    رقم التليفون : {buyer_data.phone_num} اصبح : {form.phone_num.data}
                    وصفه : {buyer_data.description} اصبح : {form.description.data}
                    الخصم : {buyer_data.discount} اصبح : {form.discount.data}
                    عدد منتجاته : {len(buyer_data.goods)}
                    اسم المستخدم الذي غير بياناته: {current_user.name}
                    الفلوس اللي عليه : {buyer_data.money_on_him} اصبحت : {buyer_data.money_on_him + buyer_data.last_collection_money - form.last_collection_money.data}
                    الفلوس اللي دفعها : {buyer_data.last_collection_money} اصبحت : {form.last_collection_money.data}
                     منشيء المشتري : {user_buyer.name}
                     لاحظ ان تم اضافة الفلوس اللي دفعها  المشتري مسبقا للمشتري مرة اخري و ثم تم خصم المبلغ الجديد المضاف""", user_id=current_user.id)

                    db.session.add(n)

                    buyer_data.money_on_him += buyer_data.last_collection_money

                    buyer_data.phone_num = form.phone_num.data
                    buyer_data.discount = form.discount.data
                    buyer_data.description = form.description.data
                    buyer_data.last_collection_money = form.last_collection_money.data

                    buyer_data.money_on_him -= buyer_data.last_collection_money

                    db.session.commit()
                    flash("نم تغير بيانات المشتري بنجاح", "success")
                    return redirect(url_for("main.home"))
                return render_template("buyer_templates/buyer_edit.html", form=form, buyer=buyer_data, user=user, page_title="عرض بيانات المشتري")
            else:
                n = Notification(notification_name=f"""شخص ما غير مسجل علي النظام حاول الدخول للصفحات المخصصة للمسؤل فقد و لكن تم حذره من قبل النظام 
                    اذا تكرر الامر برجاء مكالمة الصيانة للتبليغ عن الامر و محاولة التعامل معه""", user_id=1)
                db.session.add(n)
                db.session.commit()
                flash("انت لم تسجل بعد", "warning")
                return redirect("user.login")

@buyer.route("/get_buyer_name", methods = ["POST", "GET"], endpoint= "get_buyer_name")
@login_required
def get_buyer_name():
    form = GetBuyerNameForm()
    if form.validate_on_submit():
        buyer_ = Buyer.query.filter_by(name = form.name_buyer.data).first()
        n = Notification(notification_name=f"""تم البحث عن مشتري اسمه {buyer_.name}
        من قبل المستخدم {current_user.name}""",user_id=current_user.id)
        db.session.add(n)
        db.session.commit()
        return redirect(url_for("buyer.buyer_edit", buyer_id= buyer_.id))
    return render_template("buyer_templates/get_buyer_name.html", form = form)

# to show transaction of specific day
@buyer.route("/choose_date", methods = ["POST", "GET"], endpoint= "choose_date")
@current_user_is_admin
def choose_date():
    form = AllSalesInDate()
    if form.validate_on_submit():
        return redirect(url_for("product.sales_one_day", day= form.date.data.day, month= form.date.data.month, year= form.date.data.year))
    return render_template("product_templates/select_date.html", form = form, page_title ="عرض مبيعات تاريخ محدد")

@buyer.route("/delete_buyer_<int:buyer_id>_<string:place>", endpoint= "delete_buyer")
def delete_buyer(buyer_id, place):
    buyer_ = Buyer.query.get_or_404(buyer_id)
    user = User.query.filter_by(id = buyer_.user_created_buyer_id).first()
    if buyer_:
        try:
            user_current = User.query.filter_by(id=current_user.id).first()
        except:
            n = Notification(notification_name=f"""شخص ما غير مسجل علي النظام حاول الدخول للصفحات المخصصة للمسؤل فقد و لكن تم حذره من قبل النظام 
                اذا تكرر الامر برجاء مكالمة الصيانة للتبليغ عن الامر و محاولة التعامل معه""", user_id=1)
            db.session.add(n)
            db.session.commit()
            flash("انت لم تسجل بعد", "warning")
            return redirect(url_for("user.login"))
        else:
            if user_current:
                if user_current.IsAdmin():
                    n = Notification(notification_name=f"""تم ازالة بيانات مشتري 
                    اسم : {buyer_.name}
                    رقم تليفونه : {buyer_.phone_num}
                    وصفه : {buyer_.description}
                    خصم :{buyer_.discount} 
                    عدد منتجاته : {len(buyer_.goods)}
                    اسم المستخدم الذي ازاله: {current_user.name}
                     فلوس عليه : {buyer_.money_on_him}
                     اخر دفعة : {buyer_.last_collection_money}
                     منشيء المشتري : {user.name}
                    """, user_id=current_user.id)

                    for product in buyer_.goods:
                        db.session.delete(product)

                    db.session.add(n)
                    db.session.delete(buyer_)
                    db.session.commit()

                    flash("تم ازالة المشتري بنجاح", "success")
                    return redirect(url_for(place))
                else:
                    n = Notification(
                        notification_name=f"""لقد حاول المستخدم {user_current.name} الدخول الي الصفحات المخصصة للمسؤل فقد و النظام منعه""",
                        user_id=current_user.id)
                    db.session.add(n)
                    db.session.commit()
                    flash("انت لست مسؤل", "warning")
                    return redirect("user.login")
            else:
                n = Notification(notification_name=f"""شخص ما غير مسجل علي النظام حاول الدخول للصفحات المخصصة للمسؤل فقد و لكن تم حذره من قبل النظام 
                    اذا تكرر الامر برجاء مكالمة الصيانة للتبليغ عن الامر و محاولة التعامل معه""", user_id=1)
                db.session.add(n)
                db.session.commit()
                flash("انت لم تسجل بعد", "warning")
                return redirect("user.login")


@buyer.route("/money_collection", methods = ["POST", "GET"], endpoint= "money_collection")
@login_required
def money_collection():
    form = CollectionMoneyForm()

    list_of_buyers = Buyer.query.all()
    list_names = []
    for buyer_ in list_of_buyers:
        list_names.append(buyer_.name)
    if form.validate_on_submit():

        buyer_data = Buyer.query.filter_by(name = form.buyer_name.data).first()
        buyer_data.last_collection_money = form.money_he_pay.data
        buyer_data.last_collection_date = form.date.data
        buyer_data.last_collection_user_id = current_user.id

        buyer_data.money_on_him -= form.money_he_pay.data

        n = Notification(notification_name=f"""تم ادخال تحصيل جديد 
        اسم المستخدم الذي ادخل التحصيل : {current_user.name} 
        اسم المشتري الذي دفع التحصيل : {buyer_data.name}
        حسابه بعد التحصيل : {buyer_data.money_on_him}""", user_id=current_user.id)

        db.session.add(n)
        db.session.commit()
        flash(f"تم اضافة {buyer_data.last_collection_money} ل{buyer_data.name} بنجاح", "success")
        return redirect(url_for("main.home"))
    return render_template("buyer_templates/money_collection.html", form = form, list_names = list_names, page_title= "تسجيل تحصيل")
