from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5


@login.user_loader
def load_user(user_id):
    # First, try to load the user as a Customer
    user = Customer.query.get(int(user_id))
    if user is not None:
        return user
    # If not a Customer, try to load as a Business
    user = Business.query.get(int(user_id))
    return user

class Customer(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    vehicles: 'so.Mapped[Vehicle]' = db.relationship('Vehicle', back_populates='customer')
    bookings: 'so.Mapped[Booking]' = db.relationship('Booking', back_populates='customer')
    schedules: 'so.Mapped[Schedule]' = db.relationship('Schedule', back_populates='customer')

    def __repr__(self):
        return f'<Customer {self.username}, Email: {self.email}, ID: {self.id}>'

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

class Business(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    services: 'so.Mapped[Service]' = db.relationship('Service', back_populates='business')
    schedules: 'so.Mapped[Schedule]' = db.relationship('Schedule', back_populates='business')

    def __repr__(self):
        return f'<Business {self.username}, Email: {self.email}, ID: {self.id}>'

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Vehicle(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    make: so.Mapped[str] = so.mapped_column(sa.String(64))
    model: so.Mapped[str] = so.mapped_column(sa.String(64))
    year: so.Mapped[int] = so.mapped_column(sa.Integer)
    customer_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('customer.id'))
    customer: so.Mapped[Customer] = db.relationship('Customer', back_populates='vehicles')

    def __repr__(self):
        return f'<Vehicle ID: {self.id}, Make: {self.make}, Model: {self.model}, Year: {self.year}>'

class Service(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64))
    description: so.Mapped[str] = so.mapped_column(sa.String(256))
    price: so.Mapped[float] = so.mapped_column(sa.Float)
    business_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('business.id'))
    business: so.Mapped[Business] = db.relationship('Business', back_populates='services')
    bookings: 'so.Mapped[Booking]' = db.relationship('Booking', back_populates='service')

    def __repr__(self):
        return f'<Service ID: {self.id}, Name: {self.name}, Description: {self.description}, Price: {self.price}>'


class Schedule(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    start_time: so.Mapped[str] = so.mapped_column(sa.String(64))
    end_time: so.Mapped[str] = so.mapped_column(sa.String(64))
    business_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('business.id'))
    customer_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('customer.id'))
    business: so.Mapped[Business] = db.relationship('Business', back_populates='schedules')
    customer: so.Mapped[Customer] = db.relationship('Customer', back_populates='schedules')

    def __repr__(self):
        return f'<Schedule ID: {self.id}, Start Time: {self.start_time}, End Time: {self.end_time}>'


class Booking(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    status: so.Mapped[str] = so.mapped_column(sa.String(64))  # 'pending' or 'completed'
    customer_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('customer.id'))
    service_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('service.id'))
    customer: so.Mapped[Customer] = db.relationship('Customer', back_populates='bookings')
    service: so.Mapped[Service] = db.relationship('Service', back_populates='bookings')

    def __repr__(self):
        return f'<Booking ID: {self.id}, Status: {self.status}>'