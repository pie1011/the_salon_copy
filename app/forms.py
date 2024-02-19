from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, IntegerField, BooleanField, HiddenField, SelectMultipleField
from wtforms.fields.html5 import TelField, EmailField, DateField, TimeField
from wtforms.validators import InputRequired, DataRequired, ValidationError, Email, EqualTo, Optional, Length
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User, Appointment, GiftCard, Guest
import email_validator
from app import app, db

# stack overflow
class NewRemoteForm(FlaskForm):
    library = SelectField('Library', validators=[DataRequired()])
    model = StringField('Model', validators=[DataRequired(), Length(min=2, max=25)])
    manufacturer = StringField('Manufacturer', validators=[DataRequired(), Length(min=2, max=25)])
    type = SelectField('Type', validators=[DataRequired(), Length(min=2, max=10)])
    submit = SubmitField('Add new Remote')

    


class StylistLogin(FlaskForm):
    user_type = StringField('stylist', default='stylist', validators=[InputRequired()])
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')



class ClientLogin(FlaskForm):
    user_type = StringField('client', default='client', validators=[InputRequired()])
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField("Login")



class StylistRegister(FlaskForm):
    user_type = StringField('stylist', default='stylist', validators=[InputRequired()])
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    phone = TelField('Phone', validators=[InputRequired()])
    address_one = StringField('Address', validators=[Optional()])
    address_two = StringField('City, State', validators=[Optional()])
    birthday = DateField('Birthday', validators=[Optional()])
    preference = StringField('Preference', validators=[Optional()])
    notes = StringField('Notes', validators=[Optional()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class UserRegister(FlaskForm):
    user_type = StringField('client', default='client', validators=[InputRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = TelField('Phone', validators=[InputRequired()])
    preference = SelectField('Preferred Stylist', choices=[("None", "none"), ("Aisha", "aisha"), ("Jane", "jane"), ("Sakura", "sakura"), ("Sofia", "sofia")])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    address_one = StringField('Address', validators=[Optional()])
    address_two = StringField('City, State', validators=[Optional()])
    preference = SelectField('Stylist', validators=[Optional()])
    birthday = DateField('Birthday', validators=[Optional()])
    notes = StringField('Notes', validators=[Optional()])

    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class ScheduleForm(FlaskForm):
    client_name = StringField('Name', validators=[InputRequired()])
    date = DateField("Date", validators=[Optional()])
    time = TimeField("Time", validators=[Optional()])
    stylist_name = SelectField('Stylist')
    services = SelectMultipleField("Service", choices=[('cut', 'cut'), ('color', 'color'), ('highlight', 'highlight')])
    submit = SubmitField("Request Appointment")

class DismissNotificationForm(FlaskForm):
    submit = SubmitField('dismiss')


class ConfirmForm(FlaskForm):
    submit = SubmitField('confirm')

class CheckForm(FlaskForm):
    number = StringField('gift card code', validators=[InputRequired()])
    submit = SubmitField("Check Card")

class BuyGift(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    amount = SelectField('Amount', validators=[InputRequired()], choices=[('25.00', '$25'), ('50.00', '$50'), ('75.00', '$75'), ('100.00', '$100'), ('150.00', '$150')])
    submit = SubmitField("Purchase")

class BuyGiftGuest(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    phone = TelField('Phone', validators=[InputRequired()])
    amount = SelectField('Amount', validators=[InputRequired()], choices=[('25.00', '$25'), ('50.00', '$50'), ('75.00', '$75'), ('100.00', '$100'), ('150.00', '$150')])
    submit = SubmitField("Purchase")

class RedeemCard(FlaskForm):
    number = StringField('gift card code', validators=[InputRequired()])
    submit = SubmitField("Redeem Gift Card")

class SendCard(FlaskForm):
    card_number = StringField('gift card code', validators=[InputRequired()])
    recipient = EmailField('Recipient Email', validators=[DataRequired(), Email()])
    submit = SubmitField("Send Gift Card")


class UpdateProfile(FlaskForm):
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    phone = TelField('Phone', validators=[InputRequired()])
    address_one = StringField('Address', validators=[Optional()])
    address_two = StringField('City, State', validators=[Optional()])
    preference = SelectField('Stylist', validators=[Optional()])
    birthday = DateField('Birthday', validators=[Optional()])
    notes = StringField('Notes', validators=[Optional()])
    submit = SubmitField("Update Profile")


