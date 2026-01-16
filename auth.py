from flask import Blueprint, render_template, request, flash, redirect, url_for, session
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

# Configureer de logger voor deze module
logger = logging.getLogger(__name__)

# Maak een blueprint voor authenticatie routes
auth = Blueprint('auth', __name__)

# Route voor inloggen
@auth.route('/login', methods=['GET', 'POST'])
@limiter.limit("200 per minute")
def login():
    # Verwerk het inlogformulier
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        # Controleer of alle velden zijn ingevuld
        if not email or not password:
            flash('E-mail en wachtwoord zijn verplicht.', category='error')
            return render_template("login.html", user=current_user)

        # Controleer of het account tijdelijk is geblokkeerd door teveel foute pogingen
        is_locked, lock_message = check_failed_login_attempts(email)
        if is_locked:
            flash(lock_message, category='error')
            record_login_attempt(email, success=False)
            return render_template("login.html", user=current_user)

        # Zoek de gebruiker in de database
        user = User.query.filter_by(email=email).first()
        if user:
            # Controleer of het wachtwoord correct is
            if check_password_hash(user.password, password):
                # Update login gegevens
                user.last_login = datetime.utcnow()
                user.is_locked = False
                user.locked_until = None
                db.session.commit()
                
                # Log de gebruiker in en stel de sessie in op permanent (24 uur)
                flash('Succesvol ingelogd!', category='success')
                session.permanent = True
                login_user(user, remember=True, duration=timedelta(days=1))
                
                # Registreer de login poging en audit event
                record_login_attempt(email, success=True)
                log_audit_event(user.id, 'LOGIN', 'USER', user.id)
                logger.info(f'Succesvolle login: {email}')
                return redirect(url_for('views.home'))
            else:
                # Wachtwoord onjuist
                logger.warning(f'Foutieve wachtwoord poging voor: {email}')
                record_login_attempt(email, success=False)
                flash('Ongeldig e-mailadres of wachtwoord.', category='error')
        else:
            # Gebruiker niet gevonden
            logger.warning(f'Login poging met niet-bestaand e-mailadres: {email}')
            record_login_attempt(email, success=False)
            flash('Ongeldig e-mailadres of wachtwoord.', category='error')
    
    return render_template("login.html", user=current_user)

# Route voor registreren
@auth.route('/sign-up', methods=['GET', 'POST'])
@limiter.limit("100 per minute")
def signup():
    # Verwerk het registratieformulier
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        first_name = request.form.get('firstName', '').strip()
        password1 = request.form.get('password1', '')
        password2 = request.form.get('password2', '')
        
        # Controleer of de gebruiker al bestaat
        user = User.query.filter_by(email=email).first()
        if user:
            flash("E-mailadres bestaat al. Probeer in te loggen.", category='error')
            return render_template("sign_up.html", user=current_user, password_requirements=get_password_requirements())

        # Valideer invoerlengte
        if len(email) < 4:
            flash("E-mail moet langer zijn dan 4 karakters.", category='error')
        elif len(first_name) < 2:
            flash("Voornaam moet langer zijn dan 2 karakters.", category='error')
        elif password1 != password2:
            flash("Wachtwoorden komen niet overeen.", category='error')
        else:
            # Valideer wachtwoordcomplexiteit
            is_valid, error_msg = validate_password_complexity(password1)
            if not is_valid:
                flash(error_msg, category='error')
                return render_template("sign_up.html", user=current_user, password_requirements=get_password_requirements())
            
            try:
                # Maak nieuwe gebruiker aan met gehasht wachtwoord
                new_user = User(
                    email=email, 
                    first_name=first_name, 
                    password=generate_password_hash(password1, method='pbkdf2:sha256')
                )
                db.session.add(new_user)
                db.session.commit()
                
                # Log de nieuwe gebruiker direct in
                session.permanent = True
                login_user(new_user, remember=True)
                log_audit_event(new_user.id, 'SIGNUP', 'USER', new_user.id)
                logger.info(f'Nieuw account aangemaakt: {email}')
                flash("Account succesvol aangemaakt!", category='success')
                return redirect(url_for('views.account'))
            except IntegrityError:
                db.session.rollback()
                flash("E-mailadres bestaat al.", category='error')
            except Exception as e:
                db.session.rollback()
                logger.error(f'Registratiefout: {str(e)}')
                flash("Er is een fout opgetreden bij de registratie.", category='error')
            
    return render_template("sign_up.html", user=current_user, password_requirements=get_password_requirements())

# Route voor uitloggen
@auth.route('/logout')
@login_required
def logout():
    log_audit_event(current_user.id, 'LOGOUT', 'USER', current_user.id)
    logger.info(f'Gebruiker uitgelogd: {current_user.email}')
    logout_user()
    return redirect(url_for('auth.login'))

# Tijdelijke routes voor profiel en instellingen
@auth.route('/profile')
def profile():
    return "<p>Gebruikersprofiel</p>"

@auth.route ('/settings')
def settings():
    return "<p>Instellingen</p>"

# Route voor het uploaden van hex-bestanden naar de Microbit
@auth.route("/upload", methods=["POST"])
def upload_hex():
    file = request.files.get("hexfile")

    if not file:
        flash("Geen bestand geselecteerd.", category="error")
        return redirect(url_for("views.home"))

    skip = request.form.get("skipHandleiding")

    # Bepaal waarheen te redirecten na upload
    if skip == "true":
        return redirect(url_for("views.home"))
    else:
        return redirect(url_for("auth.handleiding"))

# Route voor de handleiding pagina
@auth.route("/handleiding")
def handleiding():
    return render_template("handleiding.html", user=current_user)
