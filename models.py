from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Pdescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    text = db.Column(db.String(10000))
    group = db.Column(db.Integer)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    date_of_birth = db.Column(db.Date)
    region = db.Column(db.String(100))
    profile_picture_path = db.Column(db.String(300))
    account_setup_complete = db.Column(db.Boolean, default=False)
    projects = db.relationship('Pdescription', backref='user')
