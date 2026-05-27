import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'main.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    from app.models import User
    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Ensure upload folder exists
    print(f"DEBUG: UPLOAD_FOLDER is set to: {app.config['UPLOAD_FOLDER']}")
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        print(f"DEBUG: Creating upload folder at {app.config['UPLOAD_FOLDER']}")
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    else:
        print("DEBUG: Upload folder already exists.")

    from app import models
    from app.routes import main
    app.register_blueprint(main)

    @app.context_processor
    def inject_globals():
        from datetime import datetime
        from app.models import Movie, TVSeason, Game, Book, Theater, Goal, FutureMediaGoal
        return {
            'datetime': datetime,
            'now': datetime.now(),
            'Movie': Movie,
            'TVSeason': TVSeason,
            'Game': Game,
            'Book': Book,
            'Theater': Theater,
            'Goal': Goal,
            'FutureMediaGoal': FutureMediaGoal
        }

    return app
