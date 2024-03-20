from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5


@login.user_loader
def load_user(id: int):
    return User.query.get(id)


class User(UserMixin):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Customer(User, db.Model):
    vehicles: 'so.Mapped[History]' = db.relationship('Vehicle', backref='customer')
    history: 'so.Mapped[History]' = db.relationship('History')

    def __repr__(self):
        return f'<Customer {self.username}, Email: {self.email}, ID: {self.id}>'


class Business(User, db.Model):
    services = db.relationship('Service', backref='business')
    history = db.relationship('History')
    price = db.relationship('Price', backref='business')

    def __repr__(self):
        return f'<Business {self.username}, Email: {self.email}, ID: {self.id}>'


class Vehicle(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    make: so.Mapped[str] = so.mapped_column(sa.String(64))
    model: so.Mapped[str] = so.mapped_column(sa.String(64))
    year: so.Mapped[int] = so.mapped_column(sa.Integer)
    customer_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('customer.id'))
    history = db.relationship('History', backref='vehicle')

    def __repr__(self):
        return f'<Vehicle ID: {self.id}, Make: {self.make}, Model: {self.model}, Year: {self.year}, Owned by ' \
               f'Customer ID: {self.customer_id}>'


class Service(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64))
    description: so.Mapped[str] = so.mapped_column(sa.String(256))
    history: 'so.Mapped[History]' = db.relationship('History', backref='service')

    def __repr__(self):
        return f'<Service ID: {self.id}, Name: {self.name}, Description: {self.description}>'


class Owner(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    customer_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('customer.id'))
    vehicle_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('vehicle.id'))
    customer: so.Mapped[Customer] = db.relationship('Customer', back_populates='vehicles')
    vehicle: so.Mapped[Vehicle] = db.relationship('Vehicle', back_populates='customer')

    def __repr__(self):
        return f'<Owner ID: {self.id}, Customer ID: {self.customer_id}, Vehicle ID: {self.vehicle_id}>'


class Price(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    service_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('service.id'))
    business_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('business.id'))
    price: so.Mapped[float] = so.mapped_column(sa.Float)
    service: so.Mapped[Service] = db.relationship('Service', back_populates='price')
    business: so.Mapped[Business] = db.relationship('Business', back_populates='price')

    def __repr__(self):
        return f'<Price ID: {self.id}, Service ID: {self.service_id}, Business ID: {self.business_id}, ' \
               f'Price: {self.price}>'


class History(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    date: so.Mapped[str] = so.mapped_column(sa.String(64))
    owner_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('owner.id'))
    service_id: so.Mapped[int] = so.mapped_column(sa.Integer)
    business_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('business.id'))
    owner: so.Mapped[Owner] = db.relationship('Owner')
    service: so.Mapped[Service] = db.relationship('Service')
    business: so.Mapped[Business] = db.relationship('Business')
    price: so.Mapped[float] = so.mapped_column(sa.Float)

    def __repr__(self):
        return f'<History ID: {self.id}, Date: {self.date}, Customer ID: {self.customer_id}, Vehicle ID: ' \
               f'{self.vehicle_id}, Service ID: {self.service_id}, Business ID: {self.business_id}>'
