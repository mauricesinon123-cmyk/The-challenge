"""Flask application factory and extension initialization."""

import os
import secrets
from datetime import timedelta

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .logger_config import setup_logging

# Initialize extensions (no app bound yet)
db = SQLAlchemy()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["500 per minute"]
)

DB_NAME = "database.db"


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Security & session configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

    # Upload limits
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
    app.config['WTF_CSRF_ENABLED'] = False  # You may enable this later

    # Database path
    app.instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    os.makedirs(app.instance_path, exist_ok=True)

    db_path = os.path.join(app.instance_path, DB_NAME)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    limiter.init_app(app)

    # Security headers
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
        response.headers["Server"] = ""
        response.headers["cache-control"] = "no-store"
        return response

    # Logging
    setup_logging(app)

    # Import blueprints INSIDE the factory to avoid cyclic imports
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Create database tables
    create_database(app)

    # Login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID."""
        from .models import User  # Local import avoids cyclic dependency
        return User.query.get(int(user_id))

    return app


def create_database(app):
    """Create the SQLite database if it does not exist."""
    db_path = os.path.join(app.instance_path, DB_NAME)
    if not os.path.exists(db_path):
        with app.app_context():
            db.create_all()
        print("Created Database!")
