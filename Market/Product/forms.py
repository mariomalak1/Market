from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, DateField
from wtforms.validators import Length, DataRequired, ValidationError
from datetime import datetime
from Market.Buyer.models import Buyer


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

class ProductEditForm(ProductForm):
    pass



