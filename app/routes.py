from app import app, db
from app.forms import StylistLogin, ClientLogin, UserRegister, ScheduleForm, ConfirmForm, CheckForm, BuyGift, BuyGiftGuest, RedeemCard, UpdateProfile, SendCard, DismissNotificationForm, NewRemoteForm
from app.models import User, Appointment, GiftCard, Guest, Service, Transaction
from flask import Flask, flash, redirect, render_template, request, session, url_for, Markup
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from datetime import date, datetime
from functools import wraps
import secrets, string, os
import re
import random

def stylist_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.is_authenticated and current_user.user_type == 'stylist':
            return f(*args, **kwargs)
        else:
            flash("You need to be logged in as a stylist.", category="alert-danger")
            return redirect(url_for('stylist_login'))
    return wrap

def client_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.is_authenticated and current_user.user_type == 'client':
            return f(*args, **kwargs)
        else:
            flash("You need to be logged in as a client.", category="alert-danger")
            return redirect(url_for('client_login'))
    return wrap

# Default Data
default_data = {
    'title':"the salon",
    'menu':{'About Us': 'index#aboutus', 'Services': 'index#services', 'Appointments': 'appointments', 'Gift Cards': 'buy_gift', 'Contact Us': 'contactus'},
    'date_now': datetime.now().strftime("%A, %B %d"),
    'today': datetime.now()
    }


@app.context_processor
def inject_data():
    data = default_data
    return dict(**data)


# INDEX
@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
def index():

    data = default_data
    data['title'] = "the salon"

    form = ClientLogin()
    
    return render_template("index.html", form=form, **data)




# LOGIN
@app.route('/stylist_login', methods=["GET", "POST"])
def stylist_login():
    """ Log the user in. """
    data = default_data
    data['title'] = "Stylist Login"

    if current_user.is_authenticated:
        check_user = current_user.user_type
        if check_user == "stylist":
            flash('You are already logged in as a stylist!', 'alert-warning')
            return redirect(url_for('index'))
        if check_user == "client":
            flash('You are already logged in as a client! Please log out to access your stylist account.', 'alert-warning')
            return redirect(url_for('index'))


    form = StylistLogin()
    if form.validate_on_submit():

        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'alert-danger')
            return redirect(url_for('stylist_login'))

        # Check what type is logging in
        check_type = db.session.query(User).filter_by(user_type=user.user_type).first()
        if check_type.user_type != 'stylist':
            flash('Invalid username or password', 'alert-danger')
            return redirect(url_for('stylist_login'))

        user.authenticated = True
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=form.remember_me.data)
        flash('You are now logged in.', 'alert-success')
        
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('account')
        return redirect(next_page)
    return render_template('stylist_login.html', form=form, **data)

# Client Login
@app.route('/client_login', methods=["GET", "POST"])
def client_login():
    """ Log the user in. """
    data = default_data
    data['title'] = "Client Login"


    if current_user.is_authenticated:
        check_user = current_user.user_type
        if check_user == "client":
            flash('You are already logged in as a client!', 'alert-warning')
            return redirect(url_for('account'))
        if check_user == "stylist":
            flash('You are already logged in as a stylist! Please log out to access your client account.', 'alert-warning')
            return redirect(url_for('index'))

    form = ClientLogin()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'alert-danger')
            return redirect(url_for('client_login'))

        # Check what type of user is logging in
        check_type = db.session.query(User).filter_by(user_type=user.user_type).first()
        if check_type.user_type != 'client':
            flash('Invalid username or password (type error)', 'alert-danger')
            return redirect(url_for('client_login'))

        user.authenticated = True
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=form.remember_me.data)
        flash('You are now logged in.', 'alert-success')

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('account')
        return redirect(next_page)
    return render_template('client_login.html', form=form,  **data)

@app.route('/logout')
def logout():
    data = default_data
    """ Log the user out. """
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    flash('You have successfully logged out.', 'alert-success')
    return redirect(url_for('index'))

@app.route('/stylist_register', methods=['GET', 'POST'])
def stylist_register():
    """ Register the user. """
    data = default_data
    data['title'] = "Stylist Registration"

    if current_user.is_authenticated:
        if current_user.user_type == 'client':
            stylist_register_form = UserRegister()

            flash(Markup('You are already logged in as a client! Please log out to register as a stylist! <a href="/logout" class="alert-link">Log out now.</a>'), 'alert-warning')
        return redirect(url_for('index'))

    
    stylists = db.session.query(User).filter_by(user_type='stylist').all()
    stylist_register_form = UserRegister()

    if stylist_register_form.validate_on_submit():
        numeric_phone = re.sub("[^0-9]", "", stylist_register_phone.phone.data)
        user = User(username=stylist_register_form.username.data,
                    email=stylist_register_form.email.data, 
                    user_type=stylist_register_form.user_type.data, 
                    phone=numeric_phone, 
                    first_name=stylist_register_form.first_name.data,
                    last_name=stylist_register_form.last_name.data,
                    birthday=stylist_register_form.birthday.data,
                    address_one=stylist_register_form.address_one.data,
                    address_two=stylist_register_form.address_two.data,
                    image='default-profile.png',
                    balance='0',
                    )
        user.set_password(stylist_register_form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'alert-success')
        return redirect(url_for('stylist_login'))
    return render_template('stylist_register.html', stylist_register_form=stylist_register_form, **data)

@app.route('/client_register', methods=['GET', 'POST'])
def client_register():
    """ Register the user. """
    data = default_data
    data['title'] = "Client Registration"

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    stylists = db.session.query(User).filter_by(user_type='stylist').all()
    client_register_form = UserRegister()
    client_register_form.preference.choices = [(stylist.username) for stylist in stylists]

    if client_register_form.validate_on_submit():
        numeric_phone = re.sub("[^0-9]", "", client_register_phone.phone.data)
        user = User(username=client_register_form.username.data,
                    email=client_register_form.email.data,
                    user_type=client_register_form.user_type.data,
                    phone=numeric_phone,
                    first_name=client_register_form.first_name.data,
                    last_name=client_register_form.last_name.data,
                    birthday=client_register_form.birthday.data,
                    address_one=client_register_form.address_one.data,
                    address_two=client_register_form.address_two.data,
                    preference=client_register_form.preference.data,
                    image='default-profile.png',
                    balance='0',
                    )
        user.set_password(client_register_form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered client!', 'alert-success')
        return redirect(url_for('client_login'))
    return render_template('client_register.html', client_register_form=client_register_form, **data)


# APPOINTMENTS
@app.route('/appointments', methods=["POST", "GET"])
def appointments():
    """ Register the user. """
    data = default_data
    data['title'] = "Request Appointment"

    stylists = db.session.query(User).filter_by(user_type='stylist').all()
    service_list = db.session.query(Service).all()

    redeem_form = RedeemCard()
    request_form = ScheduleForm()
    request_form.stylist_name.choices = [(stylist.username) for stylist in stylists]
    request_form.services.choices = [((service.name, service.name)) for service in db.session.query(Service).all()]

    if request_form.validate_on_submit():
        this_user = User.query.filter_by(id=current_user.id).first()
        appointment = Appointment(
            date=request_form.date.data, 
            time=request_form.time.data, 
            date_time=datetime.combine(request_form.date.data, request_form.time.data),
            stylist_name=request_form.stylist_name.data, 
            client_name=request_form.client_name.data, 
            requested=True, 
            confirmed=False,
            user_appointment=this_user
            )
        service_list = db.session.query(Service).all()
        accepted = []
        for choice in service_list:
            if choice.name in request_form.services.data:
                accepted.append(choice)

        appointment.services = accepted

        flash('Appointment requested!!', 'alert-success')
        db.session.add(appointment)
        db.session.commit()

        if current_user.is_authenticated:
            return redirect('account')
        else:
            return redirect('index')    
    return render_template('appointments.html', request_form=request_form, redeem_form=redeem_form, **data)

# RESCHEDULE - INCOMPLETE
@app.route('/reschedule', methods=["POST", "GET"])
def reschedule():
    """ Register the user. """
    data = default_data
    data['title'] = "Reschedule Appointment"

    stylists = db.session.query(User).filter_by(user_type='stylist').all()
    service_list = db.session.query(Service).all()

    redeem_form = RedeemCard()
    request_form = ScheduleForm()
    request_form.stylist_name.choices = [(stylist.username) for stylist in stylists]
    request_form.services.choices = [((service.name, service.name)) for service in db.session.query(Service).all()]

    if request_form.validate_on_submit():
        appointment = Appointment(
            date=request_form.date.data, 
            time=request_form.time.data, 
            date_time=datetime.combine(request_form.date.data, request_form.time.data),
            stylist_name=request_form.stylist_name.data, 
            client_name=request_form.client_name.data, 
            requested=True, 
            confirmed=False)
        service_list = db.session.query(Service).all()
        accepted = []
        for choice in service_list:
            if choice.name in request_form.services.data:
                accepted.append(choice)

        appointment.services = accepted

        flash('Appointment requested!!', 'alert-success')
        db.session.add(appointment)
        db.session.commit()

        if current_user.is_authenticated:
            return redirect('account')
        else:
            return redirect('index')    
    return render_template('appointments.html', request_form=request_form, redeem_form=redeem_form, **data)

# Confirm appointment
@app.route('/confirm_appt/<id>', methods=["POST"])
def confirm_appt(id):

    confirm_form = ConfirmForm()
    if confirm_form.validate_on_submit:
        appt = db.session.query(Appointment).filter_by(id=id).first()
        if appt is None:
            flash('Error!')
        appt.confirmed = True
        appt.requested = False
        appt.new_confirmed = True
        db.session.commit()
        flash('Confirmed!', 'alert-success')
        return redirect(url_for('account'))
    else:
        flash('I dunno?', 'alert-danger')
        return redirect(url_for('account'))


# Confirm appointment
@app.route('/dismiss_notification/<id>', methods=["POST"])
def dismiss_notification(id):

    dismiss_notification_form = DismissNotificationForm()
    if dismiss_notification_form.validate_on_submit:
        appt = db.session.query(Appointment).filter_by(id=id).first()
        if appt is None:
            flash('Error!')
        appt.new_confirmed = False
        db.session.commit()
        print('dismissed')
        return redirect(url_for('account'))
    else:
        flash('I dunno?', 'alert-danger')
        return redirect(url_for('account'))



# Gift Cards
@app.route('/check_card', methods=["POST", "GET"])
def check_card():

    data = default_data
    data['title'] = "Check Balance"

    form = CheckForm()

    if form.validate_on_submit():
        submitted = form.number.data.upper()
        num = GiftCard.query.filter_by(number=submitted).first()

        if num is None:
            flash('Invalid code', 'alert-danger')
            return redirect(url_for('check_card'))
        check = num.amount
        return render_template('check_card.html', form=form, check=check, **data)


    return render_template('check_card.html', form=form, **data)

@app.route('/redeem_card', methods=["POST", "GET"])
def redeem_card():

    redeem_form = RedeemCard()
    request_form = ScheduleForm()

    if redeem_form.validate_on_submit():
        submitted = redeem_form.number.data.upper()
        num = GiftCard.query.filter_by(number=submitted).first()

        if num is None:
            flash('Invalid code', 'alert-danger')
            return redirect(url_for('check_card'))


                     
        current_user.balance += num.amount
        num.redeemed = True
        num.redeemer_id = current_user.id
        db.session.commit()
        return redirect(url_for('account'))

    return redirect(url_for('account'))

@app.route('/redeem_card_client/<user_id>/<card_num>', methods=["POST", "GET"])
def redeem_card_client(user_id, card_num):

    num = GiftCard.query.filter_by(number=card_num).first()

    if num is None:
        flash('Invalid code', 'alert-danger')
        return redirect(url_for('check_card'))



    current_user.balance += num.amount
    num.redeemer_id = current_user.id
    num.redeemed = True
    db.session.commit()

    this_user = User.query.filter_by(id=current_user.id).first()
    new_transaction = Transaction(
        transaction_type = 'gift card redeemed - ' + card_num,
        amount = num.amount,
        user_id = this_user,
        user_transaction = this_user
    )
    db.session.add(new_transaction)
    db.session.commit()
    flash(Markup('<strong>Card redeemed!</strong> The value has been added to your balance.'), 'alert-success')
    return redirect(url_for('account'))


@app.route('/buy_gift', methods=["POST", "GET"])
def buy_gift():
    data = default_data
    data['title'] = "Buy Gift Card"

    form = BuyGift()

    if current_user.is_authenticated:
        if form.validate_on_submit():
            choices_num = string.ascii_uppercase + string.digits
            choices_con = string.digits

            random_num = ''.join(secrets.choice(choices_num) for i in range(8))
            random_con = ''.join(secrets.choice(choices_con) for i in range(8))

            new_gift = GiftCard(id=random_con, buyer_id=current_user.id, owner_id=current_user.id, number=random_num, confirm=random_con, amount=form.amount.data)

            db.session.add(new_gift)
            db.session.commit()

            flash('Card created!')
            return redirect(url_for('check_card'))
    else:
        return redirect(url_for('buy_gift_guest'))
    return render_template('buy_gift.html', form=form, **data)


@app.route('/buy_gift_guest', methods=["POST", "GET"])
def buy_gift_guest():
    
    data = default_data
    data['title'] = "Buy Gift Card"

    form = BuyGiftGuest()
        
    if form.validate_on_submit():

        choices_num = string.ascii_uppercase + string.digits
        choices_con = string.digits

        random_num = ''.join(secrets.choice(choices_num) for i in range(8))
        random_con = ''.join(secrets.choice(choices_con) for i in range(8))

        new_guest = Guest(id=random_con, name=form.name.data, email=form.email.data, phone=form.phone.data, confirm=random_con)
        new_gift = GiftCard(id=random_con, buyer_id='guest', owner_id='guest', number=random_num, confirm=random_con, amount=form.amount.data)

        db.session.add(new_guest)
        db.session.add(new_gift)
        db.session.commit()

        flash('Card created!')
        return redirect(url_for('check_card'))
    return render_template('buy_gift_guest.html', form=form, **data)


@app.route('/send_card', methods=["POST", "GET"])
def send_card():

    send_card_form = SendCard()
    if send_card_form.validate_on_submit:
        num = GiftCard.query.filter_by(number=send_card_form.card_number.data).first()
        rec = User.query.filter_by(email=send_card_form.recipient.data).first()

        if num is None:
            flash(num)
            flash('Invalid code', 'alert-danger')
            return redirect(url_for('check_card'))
                
        num.owner_id = rec.id
        db.session.commit()

        flash('You have sent the gift card!', 'alert-success')
        return redirect(url_for('account'))


# Gallery
@app.route('/gallery')
def gallery():

    data = default_data
    data['title'] = 'Gallery'

    return render_template('gallery.html', **data)




# File Uploads
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload_profile', methods=['GET', 'POST'])
def upload_profile():

    # Create random string for filename
    choices_num = string.ascii_uppercase + string.digits
    random_num = ''.join(secrets.choice(choices_num) for i in range(8))


    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file', 'alert-danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            extension = file.filename.rsplit('.', 1)[1].lower()
            filename = secure_filename(current_user.username + random_num + '.' + extension)

            old = User.query.filter_by(username=current_user.username).first()
            old_image = old.image
            if old_image != 'default-profile.png':
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], old_image))

            

            current_user.image = filename
            db.session.commit()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('account', filename=filename))
    return redirect(url_for('account'))
    '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    """ Register the user. """
    data = default_data
    data['title'] = "Update Profile"

    stylists = db.session.query(User).filter_by(user_type='stylist').all()
    profile_form = UpdateProfile()
    profile_form.preference.choices = [(stylist.username) for stylist in stylists]

    if current_user.is_authenticated:
        user = db.session.query(User).filter_by(username=current_user.username).first()

    if profile_form.validate_on_submit():
        numeric_phone = re.sub("[^0-9]", "", profile_form.phone.data)
        user.phone = numeric_phone
        user.first_name = profile_form.first_name.data
        user.last_name = profile_form.last_name.data
        user.email = profile_form.email.data
        user.address_one = profile_form.address_one.data
        user.address_two = profile_form.address_two.data
        user.preference = profile_form.preference.data
        user.birthday = profile_form.birthday.data
        user.notes = profile_form.notes.data

        db.session.add(user)
        db.session.commit()
        flash('Woo! Your profile is updated.', 'alert-success')
        return redirect(url_for('account'))
    return redirect(url_for('account'))


@app.route('/print_today', methods=['GET', 'POST'])
def print_today():
    # Set default data
    data = default_data
    data['title'] = current_user.user_type + " appointments today"
    date_now = datetime.now().strftime("%A, %B %d")
    today = datetime.now()

    user_type = 'stylist'
    if current_user.user_type == 'stylist':
        user_type = 'stylist'
    else:
        user_type = 'client'

    stylists = db.session.query(User).filter_by(user_type='stylist').all()
    clients = db.session.query(User).filter_by(preference=current_user.username).order_by(User.first_name.asc()).all()  
    service_list = db.session.query(Service).all()
    stylist_appointments = db.session.query(Appointment).filter_by(stylist_name=current_user.username).order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    stylist_appointments_today = db.session.query(Appointment).filter_by(stylist_name=current_user.username).filter(Appointment.date == datetime.utcnow().date()).order_by(Appointment.date.asc(), Appointment.time.asc()).all()



    return render_template("print_today_card.html",
        user_type=user_type,
        stylists=stylists,
        clients=clients,
        stylist_appointments=stylist_appointments, 
        stylist_appointments_today=stylist_appointments_today, 
         **data)





# View client account
@login_required
@app.route('/account', methods=["POST", "GET"])
def account():

    if not current_user.is_authenticated:
        flash('You are not logged in!', 'alert-warning')
        return redirect(url_for('client_login'))

    # Set default data
    data = default_data
    data['title'] = current_user.user_type + " Account"
    date_now = datetime.now().strftime("%A, %B %d")
    today = datetime.now()

    """ Send logged in user to account page. """

    if current_user.is_anonymous:
        flash('You are not logged in!', 'alert-warning')
        return redirect(url_for('client_login'))

    # Get User Type
    user_type = 'client'
    if current_user.user_type == 'stylist':
        user_type = 'stylist'
    else:
        user_type = 'client'
    
    # Forms
    stylists = db.session.query(User).filter_by(user_type='stylist').all()
    clients = db.session.query(User).filter_by(preference=current_user.username).order_by(User.first_name.asc()).all()  
    service_list = db.session.query(Service).all()

    client_list = {}
    confirm_form = ConfirmForm()
    profile_form = UpdateProfile()
    redeem_form = RedeemCard()
    send_card_form = SendCard()
    request_form = ScheduleForm()
    request_form.stylist_name.choices = [(stylist.username) for stylist in stylists]
    request_form.services.choices = [(service.name, service.name) for service in db.session.query(Service).all()]
    profile_form.preference.choices = [(stylist.username) for stylist in stylists]
    dismiss_notification_form = DismissNotificationForm()



    # Appointments
    client_appointments = db.session.query(Appointment).filter_by(client_name=current_user.username).order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    client_appointments_requested = db.session.query(Appointment).filter_by(client_name=current_user.username, requested=True).order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    client_appointments_confirmed = db.session.query(Appointment).filter_by(client_name=current_user.username, confirmed=True).order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    client_appointments_new_confirmed = db.session.query(Appointment).filter_by(client_name=current_user.username, new_confirmed=True).order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    stylist_appointments = db.session.query(Appointment).filter_by(stylist_name=current_user.username).order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    stylist_appointments_requested = db.session.query(Appointment).filter_by(stylist_name=current_user.username, requested=True).order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    stylist_appointments_confirmed = db.session.query(Appointment).filter_by(stylist_name=current_user.username, confirmed=True).order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    stylist_appointments_past = db.session.query(Appointment).filter_by(stylist_name=current_user.username).filter(Appointment.date_time <= datetime.now()).order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    stylist_appointments_today = db.session.query(Appointment).filter_by(stylist_name=current_user.username).filter(Appointment.date == datetime.utcnow().date()).order_by(Appointment.date.asc(), Appointment.time.asc()).all()

    next_appointment = db.session.query(Appointment).filter_by(stylist_name=current_user.username).order_by(Appointment.date.asc(), Appointment.time.asc()).first()
    stylist_requests = db.session.query(Appointment).filter_by(stylist_name=current_user.username, requested=True).filter(Appointment.date_time >= datetime.now()).order_by(Appointment.date.asc(), Appointment.time.asc()).count()
    client_requests = db.session.query(Appointment).filter_by(client_name=current_user.username, requested=True).order_by(Appointment.date.asc(), Appointment.time.asc()).count()


    # Gift Cards
    gift_cards_purchased = db.session.query(GiftCard).filter_by(buyer_id=current_user.id).all()    
    gift_cards_owned = db.session.query(GiftCard).filter_by(owner_id=current_user.id).all()    
    gift_cards_redeemed = db.session.query(GiftCard).filter_by(redeemer_id=current_user.id).all()    

    test_appt = db.session.query(User).filter_by(id=current_user.id).first()
    test_appt_data = test_appt.transactions
    test_appt_results = []
    for thing in test_appt_data:
        test_appt_results.append(thing.amount)

    # Check for notifications
    for appt in client_appointments_new_confirmed:
        if appt.client_name == current_user.username:
            appt_date = appt.date.strftime("%A, %B %d")
            appt_time = appt.time.strftime("%l:%M %p")
            notification_message = Markup('<i class="fas fa-bell"></i> &nbsp; <strong class="me-auto">Hurray!</strong><form action="/dismiss_notification/') +  str(appt.id) + Markup('" method="post"><button type="submit" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button></form></div><div class="toast-body"> Your appointment for ') + appt_date + Markup(' at ') + appt_time + Markup(' has been confirmed!')
            flash(notification_message, "notification")


    return render_template("account.html",
        user_type=user_type,
        stylists=stylists,
        clients=clients,
        service_list=service_list,
        client_appointments=client_appointments, 
        client_appointments_requested=client_appointments_requested,
        client_appointments_confirmed=client_appointments_confirmed,
        client_appointments_new_confirmed=client_appointments_new_confirmed, 
        stylist_appointments=stylist_appointments, 
        stylist_appointments_requested=stylist_appointments_requested, 
        stylist_appointments_confirmed=stylist_appointments_confirmed, 
        stylist_appointments_past=stylist_appointments_past, 
        stylist_appointments_today=stylist_appointments_today, 
        next_appointment=next_appointment,
        stylist_requests=stylist_requests,
        client_requests=client_requests,
        confirm_form=confirm_form,
        profile_form=profile_form,
        request_form=request_form, 
        redeem_form=redeem_form, 
        send_card_form=send_card_form,
        dismiss_notification_form=dismiss_notification_form,
        gift_cards_purchased=gift_cards_purchased, 
        gift_cards_redeemed=gift_cards_redeemed, 
        gift_cards_owned=gift_cards_owned)


@app.route('/card')
def card():
    data = default_data
    return render_template("stylist_account_appointment_card.html", **data)