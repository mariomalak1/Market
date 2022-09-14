from Market import db
from flask import render_template, redirect, url_for, flash, make_response, Blueprint
from Market.Buyer.forms import *
from Market.Buyer.models import Buyer
from Market.User.models import User
from Market.Main.models import Notification
from flask_login import current_user, login_required
from Market.User.routes import current_user_is_admin
import pdfkit

# Buyer routes is here

buyer = Blueprint("buyer", __name__)

@buyer.route("/make_buyer", methods = ["POST", "GET"])
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
        return redirect(url_for("buyer.make_buyer"))
    return render_template("buyer_templates/make_buyer.html", title ="make buyer", form = form, page_title ="تسجيل مشتري")


@buyer.route("/Account_statement", methods = ["POST", "GET"], endpoint= "account_statement")
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
        return redirect(url_for("buyer.account_statement_response", buyer_id= buyer.id,
        date_from_day = date_from_day, date_from_month = date_from_month, date_from_year = date_from_year,
        date_to_day = date_to_day, date_to_month = date_to_month, date_to_year = date_to_year))
    list_of_users = Buyer.query.all()
    list_names = []
    for user in list_of_users:
        list_names.append(user.name)
    return render_template("user_templates/../templates/buyer_templates/account_statement.html", list_names = list_names, form = form, page_title ="كشف حساب")


@buyer.route("/Account_statement_response/<int:buyer_id>/<int:date_from_day>/<int:date_from_month>/"
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
    rendered = render_template("buyer_templates/pdf_template.html", products = list_buyer_products, user= user, buyer = buyer)
    pdf = pdfkit.from_string(rendered, options= {"enable-local-file-access": ""},configuration = config)
    response = make_response(pdf)
    response.headers["Content-Type"] = 'application/pdf'
    response.headers["Content-Disposition"] = 'attachment; filename=output.pdf'
    flash("تم الاستخراج بنجاح", "success")
    return response


@buyer.route("/buyers_display", endpoint="buyers_display")
@current_user_is_admin
def buyers_display():
    buyers = Buyer.query.all()
    list_of_buyers = []
    for i in range(buyers[-1].id):
        user = User.query.filter_by(id = buyers[i].user_created_buyer_id).first()
        list_buyers = [buyers[i].name, buyers[i].phone_num, buyers[i].discount, i+1, user, buyers[i].id, buyers[i].money_on_him, buyers[i].money_he_pay, len(buyers[i].goods) ]
        list_of_buyers.append(list_buyers)
    return render_template("buyer_templates/buyers_display.html", buyers = list_of_buyers, page_title ="عرض المشتريين")


@buyer.route("/buyer/<int:buyer_id>/<string:place>", endpoint="buyer_edit_admin_user", methods = ["POST", "GET"])
@login_required
def buyer_edit_admin_user(buyer_id, place):
    buyer_data = Buyer.query.get_or_404(buyer_id)
    form = BuyerEditionAdminForm()
    if buyer_data:
        try:
            user = User.query.filter_by(id=current_user.id).first()
        except:
            flash("انت لم تسجل بعد", "warning")
            return redirect(url_for("user.login"))
        else:
            if user:
                if user.IsAdmin():
                    if form.validate_on_submit():
                        buyer_data.name = form.name.data
                        buyer_data.phone_num = form.phone_num.data
                        buyer_data.discount = form.discount.data
                        buyer_data.description = form.description.data
                        buyer_data.money_on_him = form.money_on_him.data
                        buyer_data.money_he_pay = form.money_he_pay.data
                        db.session.commit()
                        flash("نم تغير بيانات المشتري بنجاح", "success")
                        if place == "buyers_display":
                            return redirect(url_for("buyer.buyers_display"))
                        elif place == "today_sales":
                            return redirect(url_for("product.today_sales"))
                        elif place == "product_display":
                            return redirect(url_for("product.all_this_product"))
                        else:
                            return redirect(url_for("main.home"))
                    return render_template("buyer_templates/buyer_edit_by_admin.html", form=form, buyer=buyer_data, user=user, page_title="عرض المشتري")
            else:
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
        except:
            flash("انت لم تسجل بعد", "warning")
            return redirect(url_for("user.login"))
        else:
            if user:
                if form.validate_on_submit():
                    buyer_data.phone_num = form.phone_num.data
                    buyer_data.discount = form.discount.data
                    buyer_data.description = form.description.data
                    buyer_data.money_he_pay = form.money_he_pay.data
                    db.session.commit()
                    flash("نم تغير بيانات المشتري بنجاح", "success")
                    return redirect(url_for("main.home"))
                return render_template("buyer_templates/buyer_edit.html", form=form, buyer=buyer_data, user=user, page_title="عرض بيانات المشتري")
            else:
                flash("انت لم تسجل بعد", "warning")
                return redirect("user.login")
@buyer.route("/get_buyer_name", methods = ["POST", "GET"], endpoint= "get_buyer_name")
def get_buyer_name():
    form = GetBuyerNameForm()
    if form.validate_on_submit():
        buyer = Buyer.query.filter_by(name = form.name_buyer.data).first()
        return redirect(url_for("buyer.buyer_edit", buyer_id= buyer.id))
    return render_template("buyer_templates/get_buyer_name.html", form = form)


@buyer.route("/choose_date", methods = ["POST", "GET"], endpoint= "choose_date")
@current_user_is_admin
def choose_date():
    form = AllSalesInDate()
    if form.validate_on_submit():
        return redirect(url_for("product.sales_one_day", day= form.date.data.day, month= form.date.data.month, year= form.date.data.year))
    return render_template("product_templates/select_date.html", form = form, page_title ="عرض مبيعات تاريخ محدد")