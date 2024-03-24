from flask import render_template, flash, redirect, url_for, request
from app import app
from app.forms import LoginForm, RegistrationForm, VehicleForm, ServiceForm
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import db
from app.models import Customer, Business, Vehicle, Schedule, Service, Booking
from urllib.parse import urlsplit

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title="Home page")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        print(f"User logged in: {current_user.username}")
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(Customer).where(Customer.username == form.username.data))
        if user is None:
            user = db.session.scalar(
                sa.select(Business).where(Business.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        print(f"Logging in user: {user.username}")
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.account_type.data == 'customer':
            user = Customer(username=form.username.data, email=form.email.data)
        elif form.account_type.data == 'business':
            user = Business(username=form.username.data, email=form.email.data)
        else:
            flash('Invalid account type selected.')
            return redirect(url_for('register'))

        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    # Attempt to load a Customer first
    user_customer = Customer.query.filter_by(username=username).first()

    # If a Customer user is found
    if user_customer:
        form = VehicleForm()
        if form.validate_on_submit():
            new_vehicle = Vehicle(make=form.make.data, model=form.model.data, year=form.year.data,
                                  customer_id=user_customer.id)
            db.session.add(new_vehicle)
            db.session.commit()
            flash('Your vehicle has been added.')
            return redirect(url_for('user', username=username))
        return render_template('customer.html', user=user_customer, vehicles=user_customer.vehicles or [], form=form)

    # If no Customer is found, attempt to load a Business
    user_business = Business.query.filter_by(username=username).first_or_404()
    form = ServiceForm()
    if form.validate_on_submit():
        new_service = Service(name=form.name.data, description=form.description.data, price=form.price.data,
                              business_id=user_business.id)
        db.session.add(new_service)
        db.session.commit()
        flash('Service added successfully.')
        return redirect(url_for('user', username=username))
    return render_template('business.html', user=user_business, services=user_business.services, form=form)


@app.route('/user/<username>/add_vehicle', methods=['POST'])
@login_required
def add_vehicle(username):
    # Ensure you're retrieving the correct form and user
    form = VehicleForm()
    if form.validate_on_submit():
        user = Customer.query.filter_by(username=username).first_or_404()
        new_vehicle = Vehicle(make=form.make.data, model=form.model.data, year=form.year.data, customer_id=user.id)
        db.session.add(new_vehicle)
        db.session.commit()
        flash('Vehicle added successfully.')
        return redirect(url_for('user', username=username))
    else:
        # If the form doesn't validate, you might redirect back to the form or handle it differently
        flash('Error adding vehicle.')
        return redirect(url_for('user', username=username))

@app.route('/user/<username>/add_service', methods=['POST'])
@login_required
def add_service(username):
    form = ServiceForm()
    if form.validate_on_submit():
        business = Business.query.filter_by(username=username).first_or_404()
        new_service = Service(name=form.name.data, description=form.description.data, price=form.price.data, business=business)
        db.session.add(new_service)
        db.session.commit()
        flash('Service added successfully.')
    else:
        flash('Error adding service.')
    return redirect(url_for('user', username=username))
