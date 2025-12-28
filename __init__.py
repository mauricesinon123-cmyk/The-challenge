from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager
import secrets
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .logger_config import setup_logging
from datetime import timedelta

# Initialiseer de database en de rate limiter
db = SQLAlchemy()
limiter = Limiter(key_func=get_remote_address)
DB_NAME = "database.db"


def create_app():
    # Maak de Flask applicatie aan
    app = Flask(__name__)
    
    # Beveiligings- en sessieconfiguratie
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Stel de sessie-looptijd in op 24 uur (86400 seconden)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
    
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Configureer de database paden
    app.instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    os.makedirs(app.instance_path, exist_ok=True)
    db_path = os.path.join(app.instance_path, DB_NAME)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialiseer extensies met de app
    db.init_app(app)
    limiter.init_app(app)
    
    # Voeg beveiligingsheaders toe aan elk antwoord
    @app.after_request
    def set_response_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' code.jquery.com cdnjs.cloudflare.com maxcdn.bootstrapcdn.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com stackpath.bootstrapcdn.com; "
            "font-src 'self' https://fonts.gstatic.com https://stackpath.bootstrapcdn.com; "
            "connect-src 'self'; "
            "img-src 'self' data:"
        )
        return response

    # Configureer logging
    setup_logging(app)
    
    # Importeer en registreer blueprints
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Importeer modellen en maak de database aan
    from .models import User, Pdescription, AuditLog, LoginAttempt
    create_database(app)

    # Configureer de login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # Functie om de gebruiker te laden op basis van ID
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database(app):
    # Controleer of de database al bestaat, anders maak deze aan
    db_path = os.path.join(app.instance_path, DB_NAME)
    if not os.path.exists(db_path):
        with app.app_context():
            db.create_all()
        print('Created Database!')
