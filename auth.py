from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Pdescription
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

# Maak een blueprint voor authenticatie
auth = Blueprint('auth', __name__)

# Route voor inloggen (URL eindigt op /login)
@auth.route('/login', methods=['GET', 'POST'])
#Gebruikt login.html om vorm te geven
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Ingelogd!', category='success')
                login_user(user, remember=True, duration=timedelta(days=31))
                return redirect(url_for('views.home'))
            else:
                flash('Wachtwoord is onjuist, probeer het opnieuw.', category='error')

        else:
            flash('Email bestaat niet.', category='error')
    return render_template("login.html", user=current_user)

#Zelfde als hierboven maar dan voor sign-up
@auth.route('/sign-up', methods=['GET', 'POST'])
def signup():
    #Verwerk ingevulde data als post request binnenkomt
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email bestaat al.", category='error')

        #Validatie van de ingevulde data en voorwaarden (geeft error als iets niet klopt of voldoet)
        if len(email) <4:
            flash("Email moet langer zijn dan 4 karakters.", category='error')
        elif len(first_name) <2:
            flash("Voornaam moet langer zijn dan 2 karakters.", category='error')
        elif password1 != password2:
            flash("Wachtwoorden komen niet overeen.", category='error')
        elif len(password1) <8:
            flash("Wachtwoord moet langer zijn dan 8 karakters.", category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Account aangemaakt!", category='success')
            return redirect(url_for('views.home'))


            
    return render_template("sign_up.html", user=current_user)

#zelfde als hierboven maar dan voor logout
@auth.route('/logout')
@login_required
def logout():
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

#zelfde als hierboven maar dan voor projecten
@auth.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
    if request.method == 'POST':
        project_text = request.form.get('project', '')
        project_text = project_text.strip() if project_text is not None else ''

        if len(project_text) < 4:
            flash('Project beschrijving is te kort!', category='error')
        else:
            new_project = Pdescription(text=project_text, user_id=current_user.id)
            db.session.add(new_project)
            db.session.commit()
            flash('Project toegevoegd!', category='success')
    return render_template("projects.html", user=current_user)

@auth.route('/mijn_projecten', methods=['GET', 'POST'])
@login_required
def mijn_projecten():
    if request.method == 'POST':
        project_text = request.form.get('project', '')
        project_text = project_text.strip() if project_text is not None else ''

        if len(project_text) < 4:
            flash('Project beschrijving is te kort!', category='error')
        else:
            new_project = Pdescription(text=project_text, user_id=current_user.id)
            db.session.add(new_project)
            db.session.commit()
            flash('Project toegevoegd!', category='success')
    return render_template("mijn_projecten.html", user=current_user)


@auth.route('/wijk_projecten', methods=['GET', 'POST'])
@login_required
def wijk_projecten():
    return render_template("wijk_projecten.html", user=current_user)
