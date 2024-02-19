""" Import generic implementations for user login. """
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from app import db, login
from datetime import datetime
from hashlib import md5


@login.user_loader
def load_user(id):
    """ Loads id as int instead of string for login. """
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    """ Creates model for database. """
    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.String(20))
    username = db.Column(db.String(100), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(100))

    balance = db.Column(db.Float(300))
    image = db.Column(db.String(120))
    first_name = db.Column(db.String(120), index=True)
    last_name = db.Column(db.String(120))
    address_one = db.Column(db.String(120))
    address_two = db.Column(db.String(120))
    birthday = db.Column(db.Date)
    notes = db.Column(db.String(400))
    transactions = db.relationship('Transaction', backref='user_transaction', lazy=True)
    preference = db.Column(db.String(400))

    appointments = db.relationship('Appointment', backref='user_appointment', passive_deletes=True, lazy='dynamic')


    
    def __repr__(self, id, username, password):
        self.username = username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_stylist(self):
        if self.user_type == 'stylist':
            return True
        else:
            return False

    def is_client(self):
        if self.user_type == 'client':
            return True



class Appointment(db.Model):
    """ Creates model for database. """
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, index=True)
    time = db.Column(db.Time, index=True)
    date_time = db.Column(db.DateTime, index=True)
    time_end = db.Column(db.Time, index=True)
    services = db.Column(db.PickleType)
    requested = db.Column(db.Boolean, default=True)
    confirmed = db.Column(db.Boolean, default=False)
    new_confirmed = db.Column(db.Boolean, default=False)
    stylist_name = db.Column(db.String(80))
    client_name = db.Column(db.String(80))
    timestamp = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))


class GiftCard(UserMixin, db.Model):
    """ Creates gift card amount database. """
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, index=True)
    owner_id = db.Column(db.Integer, index=True)
    redeemer_id = db.Column(db.Integer, index=True)
    number = db.Column(db.String(80), index=True)
    confirm = db.Column(db.String(80), index=True)
    amount = db.Column(db.Float())
    redeemed = db.Column(db.Boolean, default=False)

    def __repr__(self, amount):
        self.amount = amount

class Guest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), index=True)
    email = db.Column(db.String(80), index=True)
    phone = db.Column(db.String(80), index=True)
    confirm = db.Column(db.String(80), index=True)
  
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(80), index=True)
    amount = db.Column(db.Float())
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), index=True)
    duration = db.Column(db.Integer, default='60')
    price = db.Column(db.Float())
