import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Railway provides DATABASE_URL. We also check for fallback names.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')
    
    if not SQLALCHEMY_DATABASE_URI:
        # Fallback for local development if no DB is configured
        basedir = os.path.abspath(os.path.dirname(__file__))
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
        print("WARNING: DATABASE_URL not found. Falling back to local SQLite database.")
    
    # Handle Railway's older postgres:// prefix which SQLAlchemy 1.4+ doesn't support
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-media-tracker'
    OMDB_API_KEY = os.environ.get('OMDB_API_KEY')
    TMDB_API_KEY = os.environ.get('TMDB_API_KEY')
    TMDB_READ_TOKEN = os.environ.get('TMDB_READ_TOKEN')
    
    # IGDB (Twitch) API credentials
    IGDB_CLIENT_ID = os.environ.get('IGDB_CLIENT_ID')
    IGDB_CLIENT_SECRET = os.environ.get('IGDB_CLIENT_SECRET')
    
    # Persistent storage for posters
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app', 'static', 'posters')
