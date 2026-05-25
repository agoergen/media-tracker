from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    date_watched = db.Column(db.Date)
    release_year = db.Column(db.Integer)
    is_revisit = db.Column(db.Boolean, default=False)
    external_id = db.Column(db.String(100))
    provider = db.Column(db.String(100))
    director = db.Column(db.Text)
    writer = db.Column(db.Text)
    leading_actors = db.Column(db.Text)
    plot = db.Column(db.Text)
    poster_path = db.Column(db.String(255))
    imdb_id = db.Column(db.String(20))
    user_score = db.Column(db.Float)
    runtime = db.Column(db.Integer)
    certification = db.Column(db.String(20))
    budget = db.Column(db.BigInteger)
    revenue = db.Column(db.BigInteger)
    trailer_url = db.Column(db.String(255))
    wikipedia_url = db.Column(db.String(255))

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    date_finished = db.Column(db.Date)
    release_year = db.Column(db.Integer)
    is_revisit = db.Column(db.Boolean, default=False)
    external_id = db.Column(db.String(100))
    publisher = db.Column(db.String(255))
    platform_played = db.Column(db.String(100))
    original_platform = db.Column(db.String(100))
    franchise = db.Column(db.String(255))
    status = db.Column(db.String(50)) # Backlog, In Progress, Finished, DNF

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    date_finished = db.Column(db.Date)
    release_year = db.Column(db.Integer)
    is_revisit = db.Column(db.Boolean, default=False)
    external_id = db.Column(db.String(100))
    author = db.Column(db.String(255))
    format = db.Column(db.String(100))
    goodreads_rating = db.Column(db.Integer)

class Theater(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    date_watched = db.Column(db.Date)
    release_year = db.Column(db.Integer)
    is_revisit = db.Column(db.Boolean, default=False)
    location = db.Column(db.String(255))

class TVSeason(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    series_title = db.Column(db.String(255), nullable=False)
    season_number = db.Column(db.Integer)
    date_watched = db.Column(db.Date)
    release_year = db.Column(db.Integer)
    is_revisit = db.Column(db.Boolean, default=False)
    external_id = db.Column(db.String(100))
    network = db.Column(db.String(100))
    episode_count = db.Column(db.Integer)
    poster_path = db.Column(db.String(255))
    user_score = db.Column(db.Float)
    plot = db.Column(db.Text)
    trailer_url = db.Column(db.String(255))
    imdb_id = db.Column(db.String(20))

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    format = db.Column(db.String(100))
    completed = db.Column(db.Boolean, default=False)
