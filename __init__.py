from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"


# Creeërt en configureert de flask applicatie
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'IAmASecretKeySoDontTellAnyoneWhatItIsOkay?' # Nodig voor sessies en beveiliging
    # Ensure the instance folder exists and place the DB there
    os.makedirs(app.instance_path, exist_ok=True)
    db_path = os.path.join(app.instance_path, DB_NAME)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    db.init_app(app)

    from .views import views # Importeer de views blueprint
    from .auth import auth  # Importeer de auth blueprint

    app.register_blueprint(views, url_prefix='/') # Registreer de views blueprint
    app.register_blueprint(auth, url_prefix='/') # Registreer de auth blueprint

    from .models import User, Pdescription

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