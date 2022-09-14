from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, PasswordField, BooleanField, SelectField
from wtforms.validators import Length, DataRequired, ValidationError, EqualTo
from Market.User.models import User
from flask_login import current_user
from Market import by

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
        if int(self.salary.data) < 0:
            raise ValidationError("ضع رقم صحيح")
    username_select = SelectField("اسم المستخدم الذي تريد تغير بياناته", validators=[DataRequired()], choices= choise)

class ChangeSpecificUserInformationForm(FlaskForm):
    username_selected = StringField(" اسم المستخدم الحالي", render_kw={'readonly': True})
    username = StringField('اسم المستخدم الجديد', validators=[Length(min=2, max=40)])
    phone_num = StringField("رقم التليفون الجديد")
    salary = IntegerField("المرتب الجديد", default= 0)
    admin = BooleanField("مسؤل ؟")
    submit = SubmitField("حفظ")

    def validate_phone_num(self, phone_num):
        if self.phone_num.data != "":
            if len(self.phone_num.data) != 11:
                raise ValidationError("قم بادخال رقم هاتف صحيح")
            elif self.phone_num.data[0] == '0' and self.phone_num.data[1] == '1' and (self.phone_num.data[2] == '1' or self.phone_num.data[2] == '2' or self.phone_num.data[2] == '5' or self.phone_num.data[2] == '0'):
                pass
            else:
                raise ValidationError("قم بادخال رقم هاتف صحيح")