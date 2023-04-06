from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, DateField
from wtforms.validators import Length, DataRequired, ValidationError
from datetime import datetime
from Market.Buyer.models import Buyer

class MakeBuyerForm(FlaskForm):
    name = StringField("الاسم",validators=[Length(max = 100, min= 2)])
    description = TextAreaField("وصف")
    discount = IntegerField("خصم", default= 0)
    phone_num = StringField("رقم التليفون")
    money_on_him = IntegerField("الفلوس اللي عليه", default= 0)
    last_collection_money = IntegerField("الفلوس اللي دفعها", default= 0)
    submit = SubmitField("حفظ")

    def validate_name(self, name):
        buyer = Buyer.query.filter_by(name= self.name.data).first()
        if buyer:
            raise ValidationError("هذا الاسم مستخدم من قبل برجاء كتابة الاسم اخر للتميز بينهم")

    def validate_phone_num(self, phone_num):
        if self.phone_num.data != "":
            if len(self.phone_num.data) != 11:
                raise ValidationError("قم بادخال رقم هاتف صحيح")
            elif self.phone_num.data[0] == '0' and self.phone_num.data[1] == '1' and (self.phone_num.data[2] == '1' or self.phone_num.data[2] == '2' or self.phone_num.data[2] == '5' or self.phone_num.data[2] == '0'):
                pass
            else:
                raise ValidationError("قم بادخال رقم هاتف صحيح")

    def validate_discount(self, discount):
        if int(self.discount.data) < 0:
            raise ValidationError("ضع رقم صحيح")

    def validate_money_on_him(self, money_on_him):
        if int(self.money_on_him.data) < 0:
            raise ValidationError("ضع رقم صحيح")

    def validate_last_collection_money(self, last_collection_money):
        if self.last_collection_money.data is not None:
            print(self.last_collection_money.data, self.money_on_him.data)
            if int(self.last_collection_money.data) < 0:
                raise ValidationError("ضع رقم صحيح")
            elif int(self.last_collection_money.data) > int(self.money_on_him.data):
                raise ValidationError("هل سيدفع المشتري اكثر مما اخذ؟, من فضلك غير الرقم حد اقصي الي نفس السعر الذي علي المشتري")


class GetBuyerNameForm(FlaskForm):
    name_buyer = StringField("اسم المشتري", validators=[DataRequired()])
    submit = SubmitField("بحث")

    def validate_name_buyer(self, name_buyer):
        list_user = Buyer.query.all()
        list_names = []
        for user in list_user:
            list_names.append(user.name)
        if self.name_buyer.data not in list_names:
            raise ValidationError("هذا الاسم غير موجود ضمن الاسماء المضافة, برجاء اعادة  ادخال اسم صحيح او ادخال هذا الاسم في خانة الاسامي الجديدة")

class AccountStatementForm(FlaskForm):
    buyer_name = StringField("اسم المشتري", validators=[DataRequired()])
    date_from = DateField("من تاريخ", default= datetime.now)
    date_to = DateField("الي تاريخ", default= datetime.now)
    submit = SubmitField("بحث")

    def validate_buyer_name(self, buyer_name):
        list_user = Buyer.query.all()
        list_names = []
        for user in list_user:
            list_names.append(user.name)
        if self.buyer_name.data not in list_names:
            raise ValidationError("هذا الاسم غير موجود ضمن الاسماء المضافة, برجاء اعادة  ادخال اسم صحيح او ادخال هذا الاسم في خانة الاسامي الجديدة")


    def validate_date_from(self, date_from):
        if self.date_from.data > datetime.now().date():
            raise ValidationError("لا تدخل تاريخ لم يأتي")

    def validate_date_to(self, date_to):
        if self.date_to.data > datetime.now().date():
            raise ValidationError("لا تدخل تاريخ لم يأتي")


class BuyerEditionForm(FlaskForm):
    name_non_edit = StringField("الاسم", validators=[Length(max=100, min=2)], render_kw={'readonly': True})
    money_on_him_non_edit = IntegerField("الفلوس اللي عليه", default=0, render_kw={'readonly': True})
    description = TextAreaField("وصف")
    discount = IntegerField("خصم", default=0)
    phone_num = StringField("رقم التليفون")
    last_collection_money = IntegerField("الفلوس اللي دفعها", default=0, render_kw={'readonly': True})
    submit = SubmitField("حفظ")

    def validate_phone_num(self, phone_num):
        if self.phone_num.data != "":
            if len(self.phone_num.data) != 11:
                raise ValidationError("قم بادخال رقم هاتف صحيح")
            elif self.phone_num.data[0] == '0' and self.phone_num.data[1] == '1' and (
                    self.phone_num.data[2] == '1' or self.phone_num.data[2] == '2' or self.phone_num.data[2] == '5' or
                    self.phone_num.data[2] == '0'):
                pass
            else:
                raise ValidationError("قم بادخال رقم هاتف صحيح")

    def validate_discount(self, discount):
        if int(self.discount.data) < 0:
            raise ValidationError("ضع رقم صحيح")

    def validate_last_collection_money(self, last_collection_money):
        if self.last_collection_money.data is not None:
            if int(self.last_collection_money.data) < 0 and self.last_collection_money.data > self.money_on_him_non_edit.data:
                raise ValidationError("ضع رقم صحيح")

class BuyerEditionAdminForm(MakeBuyerForm):
    def validate_name(self, name):
        buyer = Buyer.query.filter_by(name=self.name.data).first()
        if buyer and buyer.name != self.name.data:
            raise ValidationError("هذا الاسم مستخدم من قبل برجاء كتابة الاسم اخر للتميز بينهم")



class AllSalesInDate(FlaskForm):
    date = DateField("التاريخ", validators= [DataRequired()], default= datetime.now)
    submit = SubmitField("بحث")

    def validate_date(self, date):
        if self.date.data > datetime.now().date():
            raise ValidationError("لا تدخل تاريخ لم يأتي")

class CollectionMoneyForm(FlaskForm):
    buyer_name = StringField("اسم المشتري", validators=[DataRequired()])
    money_he_pay = IntegerField("اخر تحصيل", default= 0)
    date = DateField("التاريخ", validators= [DataRequired()], default= datetime.now)
    submit = SubmitField("حفظ")

    def validate_date(self, date):
        if self.date.data > datetime.now().date():
            raise ValidationError("لا تدخل تاريخ لم يأتي")

    def validate_money_he_pay(self, money_he_pay):
        if self.money_he_pay.data is not None:
            if int(self.money_he_pay.data) <= 0:
                raise ValidationError("ضع رقم صحيح")
        buyer = Buyer.query.filter_by(name = self.buyer_name.data).first()
        if buyer:
            if buyer.money_on_him < self.money_he_pay.data:
                raise ValidationError("هل سيدفع المشتري اكثر مما اخذ؟, من فضلك غير الرقم حد اقصي الي نفس السعر الذي علي المشتري")

    def validate_buyer_name(self, buyer_name):
        list_user = Buyer.query.all()
        list_names = []
        for user in list_user:
            list_names.append(user.name)
        if self.buyer_name.data not in list_names:
            raise ValidationError("هذا الاسم غير موجود ضمن الاسماء المضافة, برجاء اعادة  ادخال اسم صحيح او ادخال هذا الاسم في خانة الاسامي الجديدة")
