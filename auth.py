from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Pdescription
from datetime import timedelta, datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, limiter
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from .password_utils import validate_password_complexity, get_password_requirements
from .security_utils import (
    record_login_attempt, check_failed_login_attempts, 
    check_account_lockout, log_audit_event, get_client_ip
)
import logging

logger = logging.getLogger(__name__)

# Maak een blueprint voor authenticatie
auth = Blueprint('auth', __name__)

# Route voor inloggen (URL eindigt op /login)
@auth.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Email and password are required.', category='error')
            return render_template("login.html", user=current_user)

        is_locked, lock_message = check_failed_login_attempts(email)
        if is_locked:
            flash(lock_message, category='error')
            record_login_attempt(email, success=False)
            return render_template("login.html", user=current_user)

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                user.last_login = datetime.utcnow()
                user.is_locked = False
                user.locked_until = None
                db.session.commit()
                
                flash('Ingelogd!', category='success')
                login_user(user, remember=True, duration=timedelta(days=1))
                record_login_attempt(email, success=True)
                log_audit_event(user.id, 'LOGIN', 'USER', user.id)
                logger.info(f'Successful login: {email}')
                return redirect(url_for('views.home'))
            else:
                logger.warning(f'Failed login attempt for email: {email}')
                record_login_attempt(email, success=False)
                flash('Invalid email or password.', category='error')
        else:
            logger.warning(f'Login attempt with non-existent email: {email}')
            record_login_attempt(email, success=False)
            flash('Invalid email or password.', category='error')
    return render_template("login.html", user=current_user)

@auth.route('/sign-up', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def signup():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        first_name = request.form.get('firstName', '').strip()
        password1 = request.form.get('password1', '')
        password2 = request.form.get('password2', '')
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email bestaat al. Probeer in te loggen of gebruik een ander email adres.", category='error')
            return render_template("sign_up.html", user=current_user, password_requirements=get_password_requirements())

        if len(email) < 4:
            flash("Email moet langer zijn dan 4 karakters.", category='error')
        elif len(first_name) < 2:
            flash("Voornaam moet langer zijn dan 2 karakters.", category='error')
        elif password1 != password2:
            flash("Wachtwoorden komen niet overeen.", category='error')
        else:
            is_valid, error_msg = validate_password_complexity(password1)
            if not is_valid:
                flash(error_msg, category='error')
                return render_template("sign_up.html", user=current_user, password_requirements=get_password_requirements())
            
            try:
                new_user = User(
                    email=email, 
                    first_name=first_name, 
                    password=generate_password_hash(password1, method='pbkdf2:sha256')
                )
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                log_audit_event(new_user.id, 'SIGNUP', 'USER', new_user.id)
                logger.info(f'New account created: {email}')
                flash("Account aangemaakt!", category='success')
                return redirect(url_for('views.account'))
            except IntegrityError:
                db.session.rollback()
                logger.warning(f'Duplicate email signup attempt: {email}')
                flash("Email bestaat al. Probeer in te loggen of gebruik een ander email adres.", category='error')
            except Exception as e:
                db.session.rollback()
                logger.error(f'Signup error: {str(e)}')
                flash("An error occurred during signup. Please try again.", category='error')
            
    return render_template("sign_up.html", user=current_user, password_requirements=get_password_requirements())

@auth.route('/logout')
@login_required
def logout():
    log_audit_event(current_user.id, 'LOGOUT', 'USER', current_user.id)
    logger.info(f'User logout: {current_user.email}')
    logout_user()
    return redirect(url_for('auth.login'))

#zelfde als hierboven maar dan voor profiel
@auth.route('/profile')
def profile():
    return "<p>User Profile</p>"

#zelfde als hierboven maar dan voor instellingen
@auth.route ('/settings')
def settings():
    return "<p>Settings</p>"

