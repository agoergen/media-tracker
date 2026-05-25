from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services import OMDBService
from app.models import Movie
from app import db
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    movies = Movie.query.order_by(Movie.date_watched.desc()).limit(5).all()
    return render_template('index.html', movies=movies)

@main.route('/movies')
def movies_list():
    movies = Movie.query.order_by(Movie.date_watched.desc()).all()
    return render_template('movies.html', movies=movies)

@main.route('/movies/search', methods=['GET', 'POST'])
def search_movie():
    results = []
    query = ""
    if request.method == 'POST':
        query = request.form.get('query')
        results = OMDBService.search_movies(query)
    return render_template('movie_search.html', results=results, query=query)

@main.route('/movies/add/<imdb_id>', methods=['POST'])
def add_movie(imdb_id):
    details = OMDBService.get_movie_details(imdb_id)
    if details:
        # Basic parsing of year (OMDB sometimes returns ranges for TV, but we filtered for 'movie')
        year_str = details.get('Year', '')[:4]
        year = int(year_str) if year_str.isdigit() else None
        
        new_movie = Movie(
            title=details.get('Title'),
            release_year=year,
            external_id=imdb_id,
            director=details.get('Director'),
            leading_actors=details.get('Actors'),
            date_watched=datetime.now().date() # Default to today
        )
        db.session.add(new_movie)
        db.session.commit()
        flash(f"Added {new_movie.title} to your tracker!")
        return redirect(url_for('main.movies_list'))
    
    flash("Error fetching movie details.")
    return redirect(url_for('main.search_movie'))
