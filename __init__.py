from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager
import secrets
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .logger_config import setup_logging

db = SQLAlchemy()
limiter = Limiter(key_func=get_remote_address)
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 1800
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
    app.config['WTF_CSRF_ENABLED'] = False
    app.instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    os.makedirs(app.instance_path, exist_ok=True)
    db_path = os.path.join(app.instance_path, DB_NAME)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    limiter.init_app(app)
    
    @app.before_request
    def set_security_headers():
        from flask import make_response
        from functools import wraps
    
    @app.after_request
    def set_response_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' code.jquery.com cdnjs.cloudflare.com maxcdn.bootstrapcdn.com; style-src 'self' 'unsafe-inline' stackpath.bootstrapcdn.com; img-src 'self' data:"
        return response

    setup_logging(app)
    
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Pdescription, AuditLog, LoginAttempt

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app # Retourneer de geconfigureerde applicatie

def create_database(app):
    db_path = os.path.join(app.instance_path, DB_NAME)
    if not os.path.exists(db_path):
        with app.app_context():
            db.create_all()
        print('Created Database!')
