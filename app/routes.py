from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services import TMDBService
from app.models import Movie
from app import db
from datetime import datetime
from collections import OrderedDict

main = Blueprint('main', __name__)

@main.route('/')
def index():
    movies = Movie.query.order_by(Movie.date_watched.asc()).limit(5).all()
    return render_template('index.html', movies=movies)

@main.route('/movies')
def movies_list():
    all_movies = Movie.query.order_by(Movie.date_watched.asc()).all()
    
    # Group movies by year
    grouped = OrderedDict()
    for movie in all_movies:
        year = movie.date_watched.year if movie.date_watched else "Unknown"
        if year not in grouped:
            grouped[year] = []
        grouped[year].append(movie)
    
    return render_template('movies.html', grouped_movies=grouped, total_count=len(all_movies))

@main.route('/movies/search', methods=['GET', 'POST'])
def search_movie():
    results = []
    query = ""
    if request.method == 'POST':
        query = request.form.get('query')
        results = TMDBService.search_movies(query)
    return render_template('movie_search.html', results=results, query=query)

@main.route('/movies/add/<int:tmdb_id>', methods=['POST'])
def add_movie(tmdb_id):
    details = TMDBService.get_movie_details(tmdb_id)
    if details:
        # Extract release year
        release_date = details.get('release_date', '')
        year = int(release_date[:4]) if release_date else None
        
        # Get director and cast from credits
        credits = details.get('credits', {})
        cast = ", ".join([member.get('name') for member in credits.get('cast', [])[:5]])
        directors = ", ".join([member.get('name') for member in credits.get('crew', []) if member.get('job') == 'Director'])
        writers = ", ".join([member.get('name') for member in credits.get('crew', []) if member.get('department') == 'Writing'])
        
        # Get certification (MPAA rating)
        certification = "N/A"
        release_dates = details.get('release_dates', {}).get('results', [])
        for rd in release_dates:
            if rd.get('iso_3166_1') == 'US':
                for release in rd.get('release_dates', []):
                    cert = release.get('certification')
                    if cert:
                        certification = cert
                        break
                break
        
        # Get YouTube trailer URL
        trailer_url = None
        videos = details.get('videos', {}).get('results', [])
        for video in videos:
            if video.get('site') == 'YouTube' and video.get('type') == 'Trailer':
                trailer_url = f"https://www.youtube.com/embed/{video.get('key')}"
                break
        
        # Get external IDs (Wikipedia)
        external_ids = details.get('external_ids', {})
        wiki_id = external_ids.get('wikidata_id')
        wiki_url = f"https://www.wikidata.org/wiki/{wiki_id}" if wiki_id else None
        
        new_movie = Movie(
            title=details.get('title'),
            release_year=year,
            external_id=str(tmdb_id),
            imdb_id=details.get('imdb_id'),
            director=directors,
            writer=writers,
            leading_actors=cast,
            plot=details.get('overview'),
            poster_path=details.get('poster_path'),
            user_score=details.get('vote_average'),
            runtime=details.get('runtime'),
            certification=certification,
            budget=details.get('budget'),
            revenue=details.get('revenue'),
            trailer_url=trailer_url,
            wikipedia_url=wiki_url,
            date_watched=datetime.now().date()
        )
        db.session.add(new_movie)
        db.session.commit()
        flash(f"Added {new_movie.title} to your tracker!")
        return redirect(url_for('main.movies_list'))
    
    flash("Error fetching movie details from TMDB.")
    return redirect(url_for('main.search_movie'))

@main.route('/movies/edit/<int:movie_id>', methods=['POST'])
def edit_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    new_date_str = request.form.get('date_watched')
    if new_date_str:
        try:
            movie.date_watched = datetime.strptime(new_date_str, '%Y-%m-%d').date()
            db.session.commit()
            flash(f"Updated watch date for {movie.title}.")
        except ValueError:
            flash("Invalid date format.")
    return redirect(url_for('main.movies_list'))

@main.route('/movies/delete/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    title = movie.title
    db.session.delete(movie)
    db.session.commit()
    flash(f"Removed {title} from your tracker.")
    return redirect(url_for('main.movies_list'))
