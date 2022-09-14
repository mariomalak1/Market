from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, DateField, PasswordField, BooleanField, SelectField, HiddenField
from wtforms.validators import Length, DataRequired, ValidationError, EqualTo
from datetime import datetime
from .models import User, Buyer
from flask_login import current_user
from . import by

class MakeBuyerForm(FlaskForm):
    name = StringField("الاسم",validators=[Length(max = 100, min= 2)])
    description = TextAreaField("وصف")
    discount = IntegerField("خصم", default= 0)
    phone_num = StringField("رقم التليفون")
    money_on_him = IntegerField("الفلوس اللي عليه", default= 0)
    money_he_pay = IntegerField("الفلوس اللي دفعها", default= 0)
    submit = SubmitField("حفظ")

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

    def validate_money_he_pay(self, money_he_pay):
        if self.money_he_pay.data != None:
            if int(self.money_he_pay.data) < 0:
                raise ValidationError("ضع رقم صحيح")

class ProductForm(FlaskForm):
    name = StringField("اسم المنتج", validators=[DataRequired(), Length(max= 200, min= 2)])
    price = IntegerField("السعر بالكيلو", validators=[DataRequired()])
    name_buyer = StringField("اسم المشتري", validators=[DataRequired()])
    quantity = IntegerField("الكمية بالكيلو", validators=[DataRequired()])
    pay_quantity = IntegerField("دفع كام", default= 0)
    date = DateField("تاريخ المعاملة", default= datetime.now)
    description = TextAreaField("وصف", render_kw= {"placeholder": "وصف شيء في المعاملة"})
    submit = SubmitField("حفظ")

    def validate_price(self, price):
        if int(self.price.data) <= 0:
            raise ValidationError("ضع رقم صحيح")

    def validate_name_buyer(self, name_buyer):
        list_user = Buyer.query.all()
        list_names = []
        for user in list_user:
            list_names.append(user.name)
        if self.name_buyer.data not in list_names:
            raise ValidationError("هذا الاسم غير موجود ضمن الاسماء المضافة, برجاء اعادة  ادخال اسم صحيح او ادخال هذا الاسم في خانة الاسامي الجديدة")

    def validate_pay_quantity(self, pay_quantity):
        if int(self.pay_quantity.data) < 0:
            raise ValidationError("ضع رقم صحيح")

    def validate_quantity(self, quantity):
        if int(self.quantity.data) <= 0:
            raise ValidationError("ضع رقم صحيح")

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


# User Forms

class LoginForm(FlaskForm):
    username = StringField("اسم المستخدم")
    password = PasswordField("الرقم السري",validators=[DataRequired()])
    remember_me = BooleanField('تذكرني')
    submit = SubmitField('تسجيل دخول')

class RegistrationFrom(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired(), Length(min= 2, max= 40)])
    phone_num = StringField("رقم التليفون")
    salary = IntegerField("المرتب", default= 0)
    admin = BooleanField("مسؤل ؟")
    password = PasswordField('الرقم السري', validators=[DataRequired(),Length(min = 8, max = 50)] )
    password_confirmation = PasswordField('تاكيد الرقم السري', validators=[EqualTo('password')])
    submit = SubmitField("حفظ")

    def validate_phone_num(self, phone_num):
        if self.phone_num.data != "":
            if len(self.phone_num.data) != 11:
                raise ValidationError("قم بادخال رقم هاتف صحيح")
            elif self.phone_num.data[0] == '0' and self.phone_num.data[1] == '1' and (self.phone_num.data[2] == '1' or self.phone_num.data[2] == '2' or self.phone_num.data[2] == '5' or self.phone_num.data[2] == '0'):
                pass
            else:
                raise ValidationError("قم بادخال رقم هاتف صحيح")

class ChangePasswordUserForm(FlaskForm):
    old_password = PasswordField('الرقم السري القديم', validators=[DataRequired()])
    password = PasswordField('الرقم السري الجديد', validators=[DataRequired(), Length(min=8, max=50)])
    password_confirmation = PasswordField('تاكيد الرقم السري الجديد', validators=[EqualTo('password')])
    submit = SubmitField("حفظ")

    def validate_old_password(self, old_password):
        if by.check_password_hash(current_user.password, self.old_password.data):
            pass
        else:
            raise ValidationError("كلمة السر القديمة غير صحيحة برجاء التاكد منها")

class ChangeUserInformationForm(FlaskForm):
    @staticmethod
    def choise():
        choises_list = User.query.all()
        choises_tuple = []
        for i in choises_list:
            list_1 = []
            name, name_1 = i.name, i.name
            list_1.append(name)
            list_1.append(name_1)
            choises_tuple.append(tuple(list_1))
        return choises_tuple

    username = StringField('اسم المستخدم الجديد', validators=[Length(min=2, max=40)])
    phone_num = StringField("رقم التليفون الجديد")
    salary = IntegerField("المرتب الجديد", default= 0)
    admin = BooleanField("مسؤل ؟", default= True)
    submit = SubmitField("حفظ")

    def validate_phone_num(self, phone_num):
        if self.phone_num.data != "":
            if len(self.phone_num.data) != 11:
                raise ValidationError("قم بادخال رقم هاتف صحيح")
            elif self.phone_num.data[0] == '0' and self.phone_num.data[1] == '1' and (self.phone_num.data[2] == '1' or self.phone_num.data[2] == '2' or self.phone_num.data[2] == '5' or self.phone_num.data[2] == '0'):
                pass
            else:
                raise ValidationError("قم بادخال رقم هاتف صحيح")

    def validate_salary(self, salary):
        print(self.salary)
        if int(self.salary.data) < 0:
            raise ValidationError("ضع رقم صحيح")
    username_select = SelectField("اسم المستخدم الذي تريد تغير بياناته", validators=[DataRequired()], choices= choise)

class ChangeSpecificUserInformationForm(ChangeUserInformationForm):
    username_selected = StringField(" اسم المستخدم الحالي", render_kw={'readonly': True})

class BuyerEditionForm(MakeBuyerForm):
    name_non_edit = StringField("الاسم",validators=[Length(max = 100, min= 2)], render_kw={'readonly': True})
    money_on_him_non_edit = IntegerField("الفلوس اللي عليه", default= 0, render_kw={'readonly': True})

class ProductEditForm(ProductForm):
    pass

class AllSalesInDate(FlaskForm):
    date = DateField("التاريخ", validators= [DataRequired()], default= datetime.now)
    submit = SubmitField("بحث")

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
