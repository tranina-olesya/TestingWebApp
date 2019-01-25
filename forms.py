from flask_wtf import Form
from wtforms import StringField, PasswordField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo


class LoginForm(FlaskForm):
    login = StringField('login', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


class RegisterForm(FlaskForm):
    login = StringField('login', validators=[DataRequired(), Length(min=3)])
    first_name = StringField('first_name', validators=[DataRequired(), Length(min=2)])
    last_name = StringField('last_name', validators=[DataRequired(), Length(min=2)])
    password = PasswordField('password', validators=[DataRequired(), Length(min=4)])
    double_password = PasswordField('double_password', validators=[
        DataRequired(),
        EqualTo('password', "Пароли не совпадают"),
        Length(min=4)])