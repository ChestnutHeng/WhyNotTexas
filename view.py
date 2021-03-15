from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, FieldList, FormField
from wtforms.validators import DataRequired, EqualTo


class LoginForm(FlaskForm):
    """登录表单类"""
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    tableid = StringField('桌号（默认为1）', validators=[DataRequired()], default='1')

class SignupForm(FlaskForm):
    """用户注册表单类"""
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', [
        DataRequired(),
        EqualTo('confirm', message='两次输入的密码不一致')
    ])
    confirm = PasswordField('确认密码')

class ManageTableForm(FlaskForm):
    """登录表单类"""
    uid = StringField('')
    tableid = StringField('')
    hands = StringField('')
    username = StringField('')
    loss = StringField('')
    money = StringField('')

class ManageForm(FlaskForm):
    """登录表单类"""
    uid = StringField('uid', validators=[DataRequired()])
    tableid = StringField('table_id', validators=[DataRequired()])
    table = FieldList(FormField(ManageTableForm))