import sqlalchemy as sa
import sqlalchemy.orm as so
from app import app, db
from app.models import Customer, Business, Vehicle, Schedule, Service, Booking

@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'Customer': Customer, 'Business' : Business, 'Vehicle' : Vehicle, 'Service' : Service, 'Schedule' : Schedule, 'Booking' : Booking}