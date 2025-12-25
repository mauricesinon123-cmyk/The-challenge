from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime


class Pdescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    text = db.Column(db.String(10000), nullable=False)
    group = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)
    resource_id = db.Column(db.Integer)
    details = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())
    ip_address = db.Column(db.String(50))
    
    user = db.relationship('User', backref='audit_logs')


class LoginAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False)
    success = db.Column(db.Boolean, default=False)
    ip_address = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    date_of_birth = db.Column(db.Date)
    region = db.Column(db.String(100))
    profile_picture_path = db.Column(db.String(300))
    account_setup_complete = db.Column(db.Boolean, default=False)
    is_locked = db.Column(db.Boolean, default=False)
    locked_until = db.Column(db.DateTime(timezone=True))
    last_login = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    projects = db.relationship('Pdescription', backref='user')
