from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app
from app.services import TMDBService
from app.models import Movie, TVSeason
from app import db
from datetime import datetime
from collections import OrderedDict

main = Blueprint('main', __name__)

@main.route('/posters/<path:filename>')
def serve_poster(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

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
    
    return render_template('movies.html', grouped_movies=grouped, total_count=len(all_movies), now=datetime.now())

@main.route('/movies/search', methods=['GET', 'POST'])
def search_movie():
    results = []
    query = request.args.get('query', '')
    replace_id = request.args.get('replace_id')
    pre_date = request.args.get('pre_date', '')
    pre_loc = request.args.get('pre_loc', '')
    pre_rewatch = request.args.get('pre_rewatch', 'false')
    
    if request.method == 'POST':
        query = request.form.get('query')
        replace_id = request.form.get('replace_id')
    
    if query:
        results = TMDBService.search_movies(query)
        
    return render_template('movie_search.html', 
                         results=results, 
                         query=query, 
                         replace_id=replace_id,
                         pre_date=pre_date,
                         pre_loc=pre_loc,
                         pre_rewatch=pre_rewatch)

@main.route('/movies/add/<int:tmdb_id>', methods=['POST'])
def add_movie(tmdb_id):
    replace_id = request.form.get('replace_id')
    details = TMDBService.get_movie_details(tmdb_id)
    
    if details:
        # Get inputs from modal form (or use existing if replacing)
        date_watched_str = request.form.get('date_watched')
        watched_at = request.form.get('watched_at')
        is_rewatch_input = request.form.get('is_rewatch') == 'on'
        
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

        # Download poster for local storage
        if details.get('poster_path'):
            TMDBService.download_poster(details.get('poster_path'))

        if replace_id:
            # Update existing movie
            movie = Movie.query.get_or_404(replace_id)
            movie.title = details.get('title')
            movie.release_year = year
            movie.external_id = str(tmdb_id)
            movie.imdb_id = details.get('imdb_id')
            movie.director = directors
            movie.writer = writers
            movie.leading_actors = cast
            movie.plot = details.get('overview')
            movie.poster_path = details.get('poster_path')
            movie.user_score = details.get('vote_average')
            movie.runtime = details.get('runtime')
            movie.certification = certification
            movie.budget = details.get('budget')
            movie.revenue = details.get('revenue')
            movie.trailer_url = trailer_url
            movie.wikipedia_url = wiki_url
            
            # Keep original date/location unless explicitly provided in modal
            if date_watched_str:
                movie.date_watched = datetime.strptime(date_watched_str, '%Y-%m-%d').date()
            if watched_at:
                movie.provider = watched_at
            if request.form.get('is_rewatch'): # If form exists, update rewatch
                movie.is_revisit = is_rewatch_input
                
            flash(f"Refreshed details for {movie.title}!")
        else:
            # Add new movie
            try:
                date_watched = datetime.strptime(date_watched_str, '%Y-%m-%d').date() if date_watched_str else datetime.now().date()
            except ValueError:
                date_watched = datetime.now().date()

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
                provider=watched_at,
                is_revisit=is_rewatch_input,
                date_watched=date_watched
            )
            db.session.add(new_movie)
            flash(f"Added {new_movie.title} to your tracker!")
        
        db.session.commit()
        return redirect(url_for('main.movies_list'))
    
    flash("Error fetching movie details from TMDB.")
    return redirect(url_for('main.search_movie'))

@main.route('/movies/edit/<int:movie_id>', methods=['POST'])
def edit_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    
    # Update Date
    new_date_str = request.form.get('date_watched')
    if new_date_str:
        try:
            movie.date_watched = datetime.strptime(new_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format.")
            return redirect(url_for('main.movies_list'))

    # Update Provider (Watched At)
    movie.provider = request.form.get('watched_at')
    
    # Update Rewatch (is_revisit)
    movie.is_revisit = True if request.form.get('is_rewatch') == 'on' else False
    
    db.session.commit()
    flash(f"Updated tracking for {movie.title}.")
    return redirect(url_for('main.movies_list'))

@main.route('/movies/delete/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    title = movie.title
    db.session.delete(movie)
    db.session.commit()
    flash(f"Removed {title} from your tracker.")
    return redirect(url_for('main.movies_list'))

# TV ROUTES
@main.route('/tv')
def tv_list():
    all_seasons = TVSeason.query.order_by(TVSeason.date_watched.asc()).all()
    
    # Group by year
    grouped = OrderedDict()
    for season in all_seasons:
        year = season.date_watched.year if season.date_watched else "Unknown"
        if year not in grouped:
            grouped[year] = []
        grouped[year].append(season)
    
    return render_template('tv.html', grouped_seasons=grouped, total_count=len(all_seasons), now=datetime.now())

@main.route('/tv/search', methods=['GET', 'POST'])
def search_tv():
    results = []
    query = request.args.get('query', '')
    replace_id = request.args.get('replace_id')
    pre_date = request.args.get('pre_date', '')
    pre_loc = request.args.get('pre_loc', '')
    pre_rewatch = request.args.get('pre_rewatch', 'false')
    
    if request.method == 'POST':
        query = request.form.get('query')
        replace_id = request.form.get('replace_id')
    
    if query:
        results = TMDBService.search_tv(query)
        
    return render_template('tv_search.html', 
                         results=results, 
                         query=query, 
                         replace_id=replace_id,
                         pre_date=pre_date,
                         pre_loc=pre_loc,
                         pre_rewatch=pre_rewatch)

@main.route('/tv/add/<int:series_id>', methods=['POST'])
def add_tv_season(series_id):
    season_number = request.form.get('season_number', type=int)
    replace_id = request.form.get('replace_id')
    
    show_details = TMDBService.get_tv_show_details(series_id)
    season_details = TMDBService.get_tv_season_details(series_id, season_number)
    
    if show_details and season_details:
        # Get inputs from modal form
        date_watched_str = request.form.get('date_watched')
        watched_at = request.form.get('watched_at')
        is_rewatch_input = request.form.get('is_rewatch') == 'on'
        
        try:
            date_watched = datetime.strptime(date_watched_str, '%Y-%m-%d').date() if date_watched_str else datetime.now().date()
        except ValueError:
            date_watched = datetime.now().date()

        # Trailer (from series level usually)
        trailer_url = None
        videos = show_details.get('videos', {}).get('results', [])
        for video in videos:
            if video.get('site') == 'YouTube' and video.get('type') == 'Trailer':
                trailer_url = f"https://www.youtube.com/embed/{video.get('key')}"
                break

        # IMDB ID (from series level)
        imdb_id = show_details.get('external_ids', {}).get('imdb_id')

        # Download poster for local storage
        if details.get('poster_path'):
            TMDBService.download_poster(details.get('poster_path'))

        if replace_id:
            season = TVSeason.query.get_or_404(replace_id)
            season.series_title = show_details.get('name')
            season.season_number = season_number
            season.release_year = int(season_details.get('air_date', '')[:4]) if season_details.get('air_date') else None
            season.external_id = str(series_id)
            season.network = show_details.get('networks', [{}])[0].get('name')
            season.episode_count = len(season_details.get('episodes', []))
            season.poster_path = season_details.get('poster_path') or show_details.get('poster_path')
            season.user_score = show_details.get('vote_average')
            season.plot = season_details.get('overview') or show_details.get('overview')
            season.trailer_url = trailer_url
            season.imdb_id = imdb_id
            
            if date_watched_str:
                season.date_watched = date_watched
            if watched_at:
                season.network = watched_at # Using network as provider for TV consistency in UI
            if request.form.get('is_rewatch'):
                season.is_revisit = is_rewatch_input
                
            flash(f"Refreshed details for {season.series_title} Season {season_number}!")
        else:
            new_season = TVSeason(
                series_title=show_details.get('name'),
                season_number=season_number,
                date_watched=date_watched,
                release_year=int(season_details.get('air_date', '')[:4]) if season_details.get('air_date') else None,
                is_revisit=is_rewatch_input,
                external_id=str(series_id),
                network=watched_at or (show_details.get('networks', [{}])[0].get('name') if show_details.get('networks') else None),
                episode_count=len(season_details.get('episodes', [])),
                poster_path=season_details.get('poster_path') or show_details.get('poster_path'),
                user_score=show_details.get('vote_average'),
                plot=season_details.get('overview') or show_details.get('overview'),
                trailer_url=trailer_url,
                imdb_id=imdb_id
            )
            db.session.add(new_season)
            flash(f"Added {new_season.series_title} Season {season_number} to your tracker!")
        
        db.session.commit()
        return redirect(url_for('main.tv_list'))
    
    flash("Error fetching TV details from TMDB.")
    return redirect(url_for('main.search_tv'))

@main.route('/tv/edit/<int:season_id>', methods=['POST'])
def edit_tv_season(season_id):
    season = TVSeason.query.get_or_404(season_id)
    
    new_date_str = request.form.get('date_watched')
    if new_date_str:
        try:
            season.date_watched = datetime.strptime(new_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format.")
            return redirect(url_for('main.tv_list'))

    season.network = request.form.get('watched_at')
    season.is_revisit = True if request.form.get('is_rewatch') == 'on' else False
    
    db.session.commit()
    flash(f"Updated tracking for {season.series_title} S{season.season_number}.")
    return redirect(url_for('main.tv_list'))

@main.route('/tv/delete/<int:season_id>', methods=['POST'])
def delete_tv_season(season_id):
    season = TVSeason.query.get_or_404(season_id)
    title = f"{season.series_title} S{season.season_number}"
    db.session.delete(season)
    db.session.commit()
    flash(f"Removed {title} from your tracker.")
    return redirect(url_for('main.tv_list'))

@main.route('/backfill-tv')
def trigger_backfill_tv():
    from app.backfill_tv import run_backfill_tv
    try:
        count = run_backfill_tv()
        flash(f"Successfully backfilled {count} TV seasons!")
    except Exception as e:
        flash(f"Error during TV backfill: {str(e)}")
    return redirect(url_for('main.tv_list'))

@main.route('/scrape-movie-posters')
def trigger_scrape_movie_posters():
    from scrape_movie_posters import scrape_posters
    try:
        scrape_posters()
        flash("Successfully scraped all movie posters!")
    except Exception as e:
        flash(f"Error during poster scrape: {str(e)}")
    return redirect(url_for('main.movies_list'))
