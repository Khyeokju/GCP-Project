from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from os import path

db = SQLAlchemy()
DB_PATH = path.join(
    path.abspath(path.dirname(__file__)),
    'archive.db'
)

def create_database(app):
    if not path.exists(DB_PATH):
        with app.app_context():
            db.create_all()
        print('>>> Create DB')

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'semicircle_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Video, Employee
    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.sign_in'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app