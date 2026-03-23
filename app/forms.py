from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp

class RegistrationForm(FlaskForm):
    phone = StringField('手机号', validators=[DataRequired(), Length(11, 11), Regexp(r'^1[3-9]\d{9}$', message='请输入正确的手机号')])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[
        DataRequired(), 
        Length(min=7, max=20, message='密码长度必须大于6位'),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$', message='密码必须包含大小写字母和数字')
    ])
    submit = SubmitField('注册')

class LoginForm(FlaskForm):
    phone = StringField('手机号', validators=[DataRequired(), Length(11, 11)])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')