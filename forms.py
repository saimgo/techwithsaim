from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, FileField, EmailField
from wtforms.validators import DataRequired, Email, InputRequired
from wtforms.csrf.session import SessionCSRF

class UserLoginForm(FlaskForm):
    email = EmailField('ইমেইল', validators=[DataRequired()])
    password = PasswordField('পাসওয়ার্ড', validators=[DataRequired()])
    submit = SubmitField('লগ ইন')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    category = SelectField('Category', choices=[('Tech', 'টেক'), ('Python', 'পাইথন'), ('C++', 'সি++'), ('Problem Solving', 'প্রবলেম সল্ভিং'), ('Math', 'গণিত'), ('C', 'সি'), ('PDFs', 'পিডিএফ')], validators=[DataRequired()])
    submit = SubmitField('Submit')

class AdminLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    name = StringField('নাম', validators=[DataRequired()])
    phone = StringField('ফোন', validators=[DataRequired()])
    email = StringField('ইমেইল', validators=[DataRequired()])
    school = StringField('স্কুল/কলেজ', validators=[DataRequired()])
    image = FileField('ছবি', validators=[DataRequired()])
    password = PasswordField('পাসওয়ার্ড', validators=[DataRequired()])
    submit = SubmitField('নিবন্ধন')


class SendMessageForm(FlaskForm):
    receiver_email = StringField('Recipient\'s Email', validators=[InputRequired(), Email()])
    message = TextAreaField('Message', validators=[InputRequired()])


