from app import app, db
from app.forms import StylistLogin, ClientLogin, UserRegister, ScheduleForm, ConfirmForm, CheckForm, BuyGift, BuyGiftGuest, RedeemCard, UpdateProfile, SendCard, DismissNotificationForm
from app.models import User, Appointment, GiftCard, Guest, Service
from flask import Flask, flash, redirect, render_template, request, session, url_for, Markup
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from datetime import date, datetime
from functools import wraps
import secrets, string, os
import re

# Default Data
default_data = {
    'title':"the salon",
    'menu':{'About Us': 'index#aboutus', 'Services': 'index#services', 'Appointments': 'appointments', 'Gift Cards': 'buy_gift', 'Contact Us': 'contactus'},
    'date_now': datetime.now().strftime("%A, %B %d"),
    'today': datetime.now()
    }

##  ROUTES  ##


# ADMIN LOGIN
@app.route('/admin_login', methods=["GET", "POST"])
def admin_login():
    """ Log the user in. """
    data = default_data
    data['title'] = "Administrator Login"

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
            return redirect(url_for('admin_login'))

        # Check what type is logging in
        check_type = db.session.query(User).filter_by(user_type=user.user_type).first()
        if check_type.user_type != 'admin':
            flash('Invalid username or password', 'alert-danger')
            return redirect(url_for('admin_login'))

        user.authenticated = True
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=form.remember_me.data)
        flash('You are now logged in.', 'alert-success')
        
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('admin_account')
        return redirect(next_page)
    return render_template('admin_login.html', form=form, **data)

# ADMIN REGISTER
@app.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    """ Register the user. """
    data = default_data
    data['title'] = "Administrator Registration"

    if current_user.is_authenticated:
        if current_user.user_type == 'client' or current_user.user_type == 'stylist':
            flash(Markup('You are already logged in as a non-admin user! Please log out to register as a administrator. <a href="/logout" class="alert-link">Log out now.</a>'), 'alert-warning')
        return redirect(url_for('index'))
    
    stylists = db.session.query(User).filter_by(user_type='stylist').all()
    admin_register_form = UserRegister()

    if admin_register_form.validate_on_submit():
        numeric_phone = re.sub("[^0-9]", "", admin_register_form.phone.data)
        user = User(username=admin_register_form.username.data,
                    email=admin_register_form.email.data, 
                    user_type=admin_register_form.user_type.data, 
                    phone=numeric_phone, 
                    first_name=admin_register_form.first_name.data,
                    last_name=admin_register_form.last_name.data,
                    birthday=admin_register_form.birthday.data,
                    address_one=admin_register_form.address_one.data,
                    address_two=admin_register_form.address_two.data,
                    image='default-profile.png',
                    balance='0',
                    )
        user.set_password(admin_register_form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'alert-success')
        return redirect(url_for('admin_login'))
    return render_template('admin_register.html', admin_register_form=admin_register_form, **data)





# View admin account
@app.route('/admin_account', methods=["POST", "GET"])
def admin_account():

    date_now = datetime.now().strftime("%A, %B %d")
    today = datetime.now()


    if not current_user.is_authenticated:
        flash('You are not logged in!', 'alert-warning')
        return redirect(url_for('admin_login'))

    # User Type
    user_type = 'admin'

    # Set default data
    data = default_data
    data['title'] = "Administrator Account"

    

    # Forms
    stylists = db.session.query(User).filter_by(user_type='stylist').all()
    all_stylists = db.session.query(User).filter_by(user_type='stylist').order_by(User.first_name.asc()).all()
    all_clients = db.session.query(User).filter_by(user_type='client').order_by(User.first_name.asc()).all()  
    clients = db.session.query(User).filter_by(preference=current_user.username, user_type='client').order_by(User.first_name.asc()).all()  
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
    all_appointments = db.session.query(Appointment).order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    all_appointments_confirmed = db.session.query(Appointment).filter_by(confirmed=True).order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    all_appointments_requested = db.session.query(Appointment).filter_by(requested=True).order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    all_appointments_past = db.session.query(Appointment).filter(Appointment.date_time <= datetime.now()).order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    client_appointments = db.session.query(Appointment).filter_by(client_name=current_user.username).order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    client_appointments_requested = db.session.query(Appointment).filter_by(client_name=current_user.username, requested=True).order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    client_appointments_confirmed = db.session.query(Appointment).filter_by(client_name=current_user.username, confirmed=True).order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    client_appointments_new_confirmed = db.session.query(Appointment).filter_by(client_name=current_user.username, new_confirmed=True).order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    stylist_appointments = db.session.query(Appointment).filter_by(stylist_name=current_user.username).order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    stylist_appointments_requested = db.session.query(Appointment).filter_by(stylist_name=current_user.username, requested=True).order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    stylist_appointments_confirmed = db.session.query(Appointment).filter_by(stylist_name=current_user.username, confirmed=True).order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    stylist_appointments_past = db.session.query(Appointment).filter_by(stylist_name=current_user.username).filter(Appointment.date_time <= datetime.now()).order_by(Appointment.date.asc(), Appointment.time.asc()).all()

    next_appointment = db.session.query(Appointment).filter(Appointment.date_time >= datetime.now()).filter_by(stylist_name=current_user.username).order_by(Appointment.date.asc(), Appointment.time.asc()).first()
    all_next_appointment = db.session.query(Appointment).filter(Appointment.date_time >= datetime.now()).order_by(Appointment.date.asc(), Appointment.time.asc()).first()
    all_requests = db.session.query(Appointment).filter_by(requested=True).filter(Appointment.date_time >= datetime.now()).order_by(Appointment.date.asc(), Appointment.time.asc()).count()
    stylist_requests = db.session.query(Appointment).filter_by(stylist_name=current_user.username, requested=True).filter(Appointment.date_time >= datetime.now()).order_by(Appointment.date.asc(), Appointment.time.asc()).count()
    client_requests = db.session.query(Appointment).filter_by(client_name=current_user.username, requested=True).order_by(Appointment.date.asc(), Appointment.time.asc()).count()

    # Gift Cards
    all_gift_cards = db.session.query(GiftCard).all()    
    gift_cards_purchased = db.session.query(GiftCard).filter_by(buyer_id=current_user.id).all()    
    gift_cards_owned = db.session.query(GiftCard).filter_by(owner_id=current_user.id).all()    
    gift_cards_redeemed = db.session.query(GiftCard).filter_by(redeemer_id=current_user.id).all()    

    # Check for notifications
    for appt in client_appointments_new_confirmed:
        if appt.client_name == current_user.username:
            appt_date = appt.date.strftime("%A, %B %d")
            appt_time = appt.time.strftime("%l:%M %p")
            notification_message = Markup('<i class="fas fa-bell"></i> &nbsp; <strong class="me-auto">Hurray!</strong><form action="/dismiss_notification/') +  str(appt.id) + Markup('" method="post"><button type="submit" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button></form></div><div class="toast-body"> Your appointment for ') + appt_date + Markup(' at ') + appt_time + Markup(' has been confirmed!')
            flash(notification_message, "notification")


    return render_template("admin_account.html",
        user_type=user_type,
        stylists=stylists,
        clients=clients,
        all_stylists=all_stylists,
        all_clients=all_clients,
        service_list=service_list,
        all_appointments=all_appointments,
        all_appointments_confirmed=all_appointments_confirmed,
        all_appointments_requested=all_appointments_requested,
        all_appointments_past=all_appointments_past,
        client_appointments=client_appointments, 
        client_appointments_requested=client_appointments_requested,
        client_appointments_confirmed=client_appointments_confirmed,
        client_appointments_new_confirmed=client_appointments_new_confirmed, 
        stylist_appointments=stylist_appointments, 
        stylist_appointments_requested=stylist_appointments_requested, 
        stylist_appointments_confirmed=stylist_appointments_confirmed, 
        stylist_appointments_past=stylist_appointments_past, 
        next_appointment=next_appointment,
        all_next_appointment=all_next_appointment,
        all_requests=all_requests,
        stylist_requests=stylist_requests,
        client_requests=client_requests,
        confirm_form=confirm_form,
        profile_form=profile_form,
        request_form=request_form, 
        redeem_form=redeem_form, 
        send_card_form=send_card_form,
        dismiss_notification_form=dismiss_notification_form,
        all_gift_cards=all_gift_cards,
        gift_cards_purchased=gift_cards_purchased, 
        gift_cards_redeemed=gift_cards_redeemed, 
        gift_cards_owned=gift_cards_owned, **data)

