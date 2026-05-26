from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app
from flask_login import login_user, logout_user, current_user, login_required
from app.services import TMDBService
from app.models import Movie, TVSeason, User, Game
from app import db
from datetime import datetime
from collections import OrderedDict

main = Blueprint('main', __name__)

@main.route('/posters/<path:filename>')
def serve_poster(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user is None or not user.check_password(request.form.get('password')):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        login_user(user)
        return redirect(url_for('main.index'))
    return render_template('login.html')

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/')
def index():
    movie_count = Movie.query.count()
    tv_count = TVSeason.query.count()
    game_count = Game.query.count()
    
    # Get recent activity
    recent_movies = Movie.query.order_by(Movie.date_watched.desc()).limit(3).all()
    recent_games = Game.query.order_by(Game.date_finished.desc()).limit(3).all()
    
    return render_template('index.html', 
                         movie_count=movie_count, 
                         tv_count=tv_count, 
                         game_count=game_count,
                         recent_movies=recent_movies,
                         recent_games=recent_games,
                         now=datetime.now())

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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
        if season_details.get('poster_path'):
            TMDBService.download_poster(season_details.get('poster_path'))
        elif show_details.get('poster_path'):
            TMDBService.download_poster(show_details.get('poster_path'))

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
@login_required
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
@login_required
def delete_tv_season(season_id):
    season = TVSeason.query.get_or_404(season_id)
    title = f"{season.series_title} S{season.season_number}"
    db.session.delete(season)
    db.session.commit()
    flash(f"Removed {title} from your tracker.")
    return redirect(url_for('main.tv_list'))

# GAME ROUTES
from app.services import IGDBService

@main.route('/games')
def games_list():
    all_games = Game.query.order_by(Game.date_finished.asc()).all()
    
    # Group by year
    grouped = OrderedDict()
    for game in all_games:
        year = game.date_finished.year if game.date_finished else "Unknown"
        if year not in grouped:
            grouped[year] = []
        grouped[year].append(game)
    
    return render_template('games.html', grouped_games=grouped, total_count=len(all_games), now=datetime.now())

@main.route('/games/search', methods=['GET', 'POST'])
@login_required
def search_game():
    results = []
    query = request.args.get('query', '')
    replace_id = request.args.get('replace_id')
    pre_date = request.args.get('pre_date', '')
    pre_plat = request.args.get('pre_plat', '')
    pre_rewatch = request.args.get('pre_rewatch', 'false')
    pre_variant = request.args.get('pre_variant', '')
    
    if request.method == 'POST':
        query = request.form.get('query')
        replace_id = request.form.get('replace_id')
    
    if query:
        results = IGDBService.search_games(query)
        
    return render_template('game_search.html', 
                         results=results, 
                         query=query, 
                         replace_id=replace_id,
                         pre_date=pre_date,
                         pre_plat=pre_plat,
                         pre_rewatch=pre_rewatch,
                         pre_variant=pre_variant,
                         datetime=datetime)

@main.route('/games/add/<int:igdb_id>', methods=['POST'])
@login_required
def add_game(igdb_id):
    replace_id = request.form.get('replace_id')
    details = IGDBService.get_game_details(igdb_id)
    
    if details:
        # Get inputs from modal form
        date_finished_str = request.form.get('date_finished')
        platform_played = request.form.get('platform_played')
        is_rewatch = True if request.form.get('is_rewatch') == 'on' else False
        variant = request.form.get('variant')
        
        try:
            date_finished = datetime.strptime(date_finished_str, '%Y-%m-%d').date() if date_finished_str else datetime.now().date()
        except ValueError:
            date_finished = datetime.now().date()

        # Extract basic info
        release_date_ts = details.get('first_release_date')
        release_year = datetime.fromtimestamp(release_date_ts).year if release_date_ts else None
        
        # Companies
        involved = details.get('involved_companies', [])
        developers = ", ".join([ic['company']['name'] for ic in involved if ic.get('developer')])
        publishers = ", ".join([ic['company']['name'] for ic in involved if ic.get('publisher')])
        
        # Cover
        cover_filename = None
        if details.get('cover'):
            cover_filename = IGDBService.download_cover(details['cover']['url'])

        if replace_id:
            game = Game.query.get_or_404(replace_id)
            game.title = details.get('name')
            game.release_year = release_year
            game.external_id = str(igdb_id)
            game.developer = developers
            game.publisher = publishers
            game.franchise = ", ".join([f['name'] for f in details.get('franchises', [])])
            game.summary = details.get('summary')
            game.genres = ", ".join([g['name'] for g in details.get('genres', [])])
            game.user_score = details.get('rating')
            game.critic_score = details.get('aggregated_rating')
            game.poster_path = cover_filename
            
            if date_finished_str:
                game.date_finished = date_finished
            if platform_played:
                game.platform_played = platform_played
            if request.form.get('is_rewatch'):
                game.is_revisit = is_rewatch
            if variant:
                game.variant = variant
                
            flash(f"Refreshed details for {game.title}!")
        else:
            new_game = Game(
                title=details.get('name'),
                release_year=release_year,
                external_id=str(igdb_id),
                developer=developers,
                publisher=publishers,
                franchise=", ".join([f['name'] for f in details.get('franchises', [])]),
                summary=details.get('summary'),
                genres=", ".join([g['name'] for g in details.get('genres', [])]),
                user_score=details.get('rating'),
                critic_score=details.get('aggregated_rating'),
                poster_path=cover_filename,
                platform_played=platform_played,
                original_platform=", ".join([p['name'] for p in details.get('platforms', [])[:3]]),
                is_revisit=is_rewatch,
                variant=variant,
                date_finished=date_finished,
                status='Finished'
            )
            db.session.add(new_game)
            flash(f"Added {new_game.title} to your tracker!")
        
        db.session.commit()
        return redirect(url_for('main.games_list'))
    
    flash("Error fetching game details from IGDB.")
    return redirect(url_for('main.search_game'))

@main.route('/games/edit/<int:game_id>', methods=['POST'])
@login_required
def edit_game(game_id):
    game = Game.query.get_or_404(game_id)
    
    date_str = request.form.get('date_finished')
    if date_str:
        try:
            game.date_finished = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format.")
            return redirect(url_for('main.games_list'))

    game.platform_played = request.form.get('platform_played')
    game.variant = request.form.get('variant')
    game.is_revisit = True if request.form.get('is_rewatch') == 'on' else False
    
    db.session.commit()
    flash(f"Updated tracking for {game.title}.")
    return redirect(url_for('main.games_list'))

@main.route('/games/delete/<int:game_id>', methods=['POST'])
@login_required
def delete_game(game_id):
    game = Game.query.get_or_404(game_id)
    title = game.title
    db.session.delete(game)
    db.session.commit()
    flash(f"Removed {title} from your tracker.")
    return redirect(url_for('main.games_list'))

@main.route('/backfill-games')
def trigger_backfill_games():
    from app.backfill_games import run_backfill_games
    try:
        count = run_backfill_games()
        flash(f"Successfully backfilled {count} games!")
    except Exception as e:
        flash(f"Error during game backfill: {str(e)}")
    return redirect(url_for('main.games_list'))
