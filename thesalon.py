""" Bring in app and db. """
from app import app, db
from app.models import User, Appointment, GiftCard, Guest, Service

@app.shell_context_processor
def make_shell_context():
    """ Shell context for database. """
    return {'db': db, 'User': User, 'Appointment': Appointment, 'GiftCard': GiftCard, 'Guest': Guest, 'Service': Service}
