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

    # Synchronize PostgreSQL primary key sequences on startup to prevent ID collisions
    import sqlalchemy as sa
    with app.app_context():
        if db.engine.dialect.name == 'postgresql':
            tables = ['user', 'movie', 'game', 'book', 'theater', 'tv_season', 'goal', 'future_media_goal', 'backlog_item', 'invite_token']
            with db.engine.connect() as conn:
                for tbl in tables:
                    try:
                        conn.execute(sa.text(f"SELECT setval(pg_get_serial_sequence('\"{tbl}\"', 'id'), COALESCE((SELECT MAX(id) FROM \"{tbl}\"), 1));"))
                        conn.commit()
                    except Exception:
                        pass

    @app.context_processor
    def inject_globals():
        from datetime import datetime
        from app.models import Movie, TVSeason, Game, Book, Theater, Goal, FutureMediaGoal, BacklogItem
        from app.services import safe_from_timestamp
        
        # Build a map of target titles for efficient lookup in templates
        # Format: {(year, category, title.lower()): True}
        try:
            from flask_login import current_user
            if current_user.is_authenticated:
                all_targets = FutureMediaGoal.query.filter_by(user_id=current_user.id).all()
            else:
                admin_user = User.query.filter_by(is_admin=True).order_by(User.id.asc()).first()
                admin_uid = admin_user.id if admin_user else 1
                all_targets = FutureMediaGoal.query.filter_by(user_id=admin_uid).all()
            target_map = {(tg.year, tg.category, tg.title.lower()): True for tg in all_targets}
        except Exception:
            target_map = {}

        return {
            'datetime': datetime,
            'safe_from_timestamp': safe_from_timestamp,
            'now': datetime.now(),
            'Movie': Movie,
            'TVSeason': TVSeason,
            'Game': Game,
            'Book': Book,
            'Theater': Theater,
            'Goal': Goal,
            'FutureMediaGoal': FutureMediaGoal,
            'BacklogItem': BacklogItem,
            'target_map': target_map,
            'is_prod': app.config.get('IS_PROD', False),
            'env_name': app.config.get('ENV_NAME', 'DEV')
        }

    return app
