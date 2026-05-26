from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app
from flask_login import login_user, logout_user, current_user, login_required
from app.services import TMDBService, IGDBService, OpenLibraryService, GoogleBooksService, ImageSearchService, WikipediaService, IBDBService
from app.models import Movie, TVSeason, User, Game, Book, Theater
from app import db
from datetime import datetime
from collections import OrderedDict

main = Blueprint('main', __name__)

@main.route('/posters/<path:filename>')
def serve_poster(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.index'))
        flash('Invalid username or password')
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/')
def index():
    # Latest 5 of each category
    recent_movies = Movie.query.order_by(Movie.date_watched.desc()).limit(5).all()
    movie_count = Movie.query.count()
    
    recent_games = Game.query.order_by(Game.date_finished.desc()).limit(5).all()
    game_count = Game.query.count()

    recent_tv = TVSeason.query.order_by(TVSeason.date_watched.desc()).limit(5).all()
    tv_count = TVSeason.query.count()

    current_year = datetime.now().year
    movies_this_year = Movie.query.filter(db.extract('year', Movie.date_watched) == current_year).count()
    games_this_year = Game.query.filter(db.extract('year', Game.date_finished) == current_year).count()
    tv_this_year = TVSeason.query.filter(db.extract('year', TVSeason.date_watched) == current_year).count()
    books_this_year = Book.query.filter(db.extract('year', Book.date_finished) == current_year).count()
    theater_this_year = Theater.query.filter(db.extract('year', Theater.date_watched) == current_year).count()
    
    recent_theater = Theater.query.order_by(Theater.date_watched.desc()).limit(5).all()

    return render_template('index.html', 
                         recent_movies=recent_movies, 
                         movie_count=movie_count,
                         movies_this_year=movies_this_year,
                         recent_games=recent_games,
                         game_count=game_count,
                         games_this_year=games_this_year,
                         recent_tv=recent_tv,
                         tv_count=tv_count,
                         tv_this_year=tv_this_year,
                         books_this_year=books_this_year,
                         theater_this_year=theater_this_year,
                         recent_theater=recent_theater)

# MOVIE ROUTES
@main.route('/movies')
def movies_list():
    all_movies = Movie.query.order_by(Movie.date_watched.asc()).all()
    
    # Group by year
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
        # Get inputs from modal form
        date_watched_str = request.form.get('date_watched')
        watched_at = request.form.get('watched_at')
        is_rewatch_input = True if request.form.get('is_rewatch') == 'on' else False
        
        try:
            date_watched = datetime.strptime(date_watched_str, '%Y-%m-%d').date() if date_watched_str else datetime.now().date()
        except ValueError:
            date_watched = datetime.now().date()

        # Extract basic info
        release_year = int(details.get('release_date', '0')[:4]) if details.get('release_date') else None
        
        # Crew & Cast
        credits = details.get('credits', {})
        crew = credits.get('crew', [])
        cast = credits.get('cast', [])
        
        director = ", ".join([c['name'] for c in crew if c['job'] == 'Director'])
        writer = ", ".join([c['name'] for c in crew if c['job'] in ['Screenplay', 'Writer']])
        leading_actors = ", ".join([c['name'] for c in cast[:5]])

        # Poster
        poster_filename = None
        if details.get('poster_path'):
            poster_filename = TMDBService.download_poster(details['poster_path'])

        if replace_id:
            movie = Movie.query.get_or_404(replace_id)
            movie.title = details.get('title')
            movie.release_year = release_year
            movie.external_id = str(tmdb_id)
            movie.director = director
            movie.writer = writer
            movie.leading_actors = leading_actors
            movie.plot = details.get('overview')
            movie.poster_path = poster_filename
            movie.imdb_id = details.get('imdb_id')
            movie.user_score = details.get('vote_average')
            movie.runtime = details.get('runtime')
            # Certification (Safe extraction)
            release_results = details.get('release_dates', {}).get('results', [])
            us_release = next((r for r in release_results if r['iso_3166_1'] == 'US'), {})
            certification = next((rd.get('certification') for rd in us_release.get('release_dates', []) if rd.get('certification')), None)

            movie.certification = certification
            movie.budget = details.get('budget')
            movie.revenue = details.get('revenue')
            
            # Extract trailer
            videos = details.get('videos', {}).get('results', [])
            trailer = next((v['key'] for v in videos if v['type'] == 'Trailer' and v['site'] == 'YouTube'), None)
            if trailer:
                movie.trailer_url = f"https://www.youtube.com/embed/{trailer}"

            # Wikipedia/Wikidata
            wikidata_id = details.get('external_ids', {}).get('wikidata_id')
            if wikidata_id:
                movie.wikipedia_url = f"https://www.wikidata.org/wiki/{wikidata_id}"
            
            if date_watched_str:
                movie.date_watched = date_watched
            if watched_at:
                movie.provider = watched_at
            if request.form.get('is_rewatch'):
                movie.is_revisit = is_rewatch_input
                
            flash(f"Refreshed details for {movie.title}!")
        else:
            new_movie = Movie(
                title=details.get('title'),
                date_watched=date_watched,
                release_year=release_year,
                external_id=str(tmdb_id),
                provider=watched_at,
                is_revisit=is_rewatch_input,
                director=director,
                writer=writer,
                leading_actors=leading_actors,
                plot=details.get('overview'),
                poster_path=poster_filename,
                imdb_id=details.get('imdb_id'),
                user_score=details.get('vote_average'),
                runtime=details.get('runtime'),
                certification=next((rd.get('certification') for rd in next((r for r in details.get('release_dates', {}).get('results', []) if r['iso_3166_1'] == 'US'), {}).get('release_dates', []) if rd.get('certification')), None),
                budget=details.get('budget'),
                revenue=details.get('revenue')
            )
            
            videos = details.get('videos', {}).get('results', [])
            trailer = next((v['key'] for v in videos if v['type'] == 'Trailer' and v['site'] == 'YouTube'), None)
            if trailer:
                new_movie.trailer_url = f"https://www.youtube.com/embed/{trailer}"

            wikidata_id = details.get('external_ids', {}).get('wikidata_id')
            if wikidata_id:
                new_movie.wikipedia_url = f"https://www.wikidata.org/wiki/{wikidata_id}"

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
    
    date_str = request.form.get('date_watched')
    if date_str:
        try:
            movie.date_watched = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format.")
            return redirect(url_for('main.movies_list'))

    movie.provider = request.form.get('watched_at')
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
    pre_season = request.args.get('pre_season', '1')

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
                         pre_rewatch=pre_rewatch,
                         pre_season=pre_season)

@main.route('/tv/add/<int:series_id>', methods=['POST'])
@login_required
def add_tv_season(series_id):
    replace_id = request.form.get('replace_id')
    season_number = int(request.form.get('season_number', 1))
    
    details = TMDBService.get_tv_details(series_id, season_number)
    
    if details:
        date_watched_str = request.form.get('date_watched')
        watched_at = request.form.get('watched_at')
        is_rewatch_input = True if request.form.get('is_rewatch') == 'on' else False
        
        try:
            date_watched = datetime.strptime(date_watched_str, '%Y-%m-%d').date() if date_watched_str else datetime.now().date()
        except ValueError:
            date_watched = datetime.now().date()

        poster_filename = None
        if details.get('poster_path'):
            poster_filename = TMDBService.download_poster(details['poster_path'])

        if replace_id:
            season = TVSeason.query.get_or_404(replace_id)
            season.series_title = details.get('series_name')
            season.season_number = season_number
            season.external_id = str(series_id)
            season.network = details.get('network')
            season.episode_count = details.get('episode_count')
            season.poster_path = poster_filename
            season.user_score = details.get('vote_average')
            season.plot = details.get('overview')
            
            videos = details.get('videos', {}).get('results', [])
            trailer = next((v['key'] for v in videos if v['type'] == 'Trailer' and v['site'] == 'YouTube'), None)
            if trailer:
                season.trailer_url = f"https://www.youtube.com/embed/{trailer}"
            
            if date_watched_str:
                season.date_watched = date_watched
            if watched_at:
                season.network = watched_at
            if request.form.get('is_rewatch'):
                season.is_revisit = is_rewatch_input
                
            flash(f"Refreshed details for {season.series_title} S{season.season_number}!")
        else:
            new_season = TVSeason(
                series_title=details.get('series_name'),
                season_number=season_number,
                date_watched=date_watched,
                external_id=str(series_id),
                network=watched_at or details.get('network'),
                episode_count=details.get('episode_count'),
                poster_path=poster_filename,
                user_score=details.get('vote_average'),
                plot=details.get('overview'),
                is_revisit=is_rewatch_input
            )
            
            videos = details.get('videos', {}).get('results', [])
            trailer = next((v['key'] for v in videos if v['type'] == 'Trailer' and v['site'] == 'YouTube'), None)
            if trailer:
                new_season.trailer_url = f"https://www.youtube.com/embed/{trailer}"

            db.session.add(new_season)
            flash(f"Added {new_season.series_title} Season {new_season.season_number} to your tracker!")
        
        db.session.commit()
        return redirect(url_for('main.tv_list'))
    
    flash("Error fetching TV details from TMDB.")
    return redirect(url_for('main.search_tv'))

@main.route('/tv/edit/<int:season_id>', methods=['POST'])
@login_required
def edit_tv_season(season_id):
    season = TVSeason.query.get_or_404(season_id)
    
    date_str = request.form.get('date_watched')
    if date_str:
        try:
            season.date_watched = datetime.strptime(date_str, '%Y-%m-%d').date()
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
@main.route('/games')
def games_list():
    all_games = Game.query.order_by(Game.date_finished.asc()).all()
    
    distinct_franchises = db.session.query(Game.franchise).distinct().filter(Game.franchise.isnot(None), Game.franchise != '').order_by(Game.franchise).all()
    franchise_list = [f[0] for f in distinct_franchises]
    
    grouped = OrderedDict()
    for game in all_games:
        year = game.date_finished.year if game.date_finished else "Unknown"
        if year not in grouped:
            grouped[year] = []
        grouped[year].append(game)
    
    return render_template('games.html', grouped_games=grouped, total_count=len(all_games), now=datetime.now(), distinct_franchises=franchise_list)

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
    
    distinct_franchises = db.session.query(Game.franchise).distinct().filter(Game.franchise.isnot(None), Game.franchise != '').order_by(Game.franchise).all()
    franchise_list = [f[0] for f in distinct_franchises]
    
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
                         datetime=datetime,
                         distinct_franchises=franchise_list)

@main.route('/games/add/<int:igdb_id>', methods=['POST'])
@login_required
def add_game(igdb_id):
    replace_id = request.form.get('replace_id')
    details = IGDBService.get_game_details(igdb_id)
    
    if details:
        date_finished_str = request.form.get('date_finished')
        platform_played = request.form.get('platform_played')
        is_rewatch = True if request.form.get('is_rewatch') == 'on' else False
        variant = request.form.get('variant')
        franchise_input = request.form.get('franchise')
        
        try:
            date_finished = datetime.strptime(date_finished_str, '%Y-%m-%d').date() if date_finished_str else datetime.now().date()
        except ValueError:
            date_finished = datetime.now().date()

        release_date_ts = details.get('first_release_date')
        release_year = datetime.fromtimestamp(release_date_ts).year if release_date_ts else None
        
        involved = details.get('involved_companies', [])
        developers = ", ".join([ic['company']['name'] for ic in involved if ic.get('developer')])
        publishers = ", ".join([ic['company']['name'] for ic in involved if ic.get('publisher')])
        
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
            game.franchise = franchise_input or ", ".join([f['name'] for f in details.get('franchises', [])])
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
            if franchise_input:
                game.franchise = franchise_input
                
            flash(f"Refreshed details for {game.title}!")
        else:
            new_game = Game(
                title=details.get('name'),
                release_year=release_year,
                external_id=str(igdb_id),
                developer=developers,
                publisher=publishers,
                franchise=franchise_input or ", ".join([f['name'] for f in details.get('franchises', [])]),
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
    game.franchise = request.form.get('franchise')
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


# BOOK ROUTES
@main.route('/books')
def books_list():
    all_books = Book.query.order_by(Book.date_finished.asc()).all()
    
    grouped = OrderedDict()
    for book in all_books:
        year = book.date_finished.year if book.date_finished else "Unknown"
        if year not in grouped:
            grouped[year] = []
        grouped[year].append(book)
    
    return render_template('books.html', grouped_books=grouped, total_count=len(all_books), now=datetime.now())

@main.route('/books/search', methods=['GET', 'POST'])
@login_required
def search_book():
    results = []
    query = request.args.get('query', '')
    replace_id = request.args.get('replace_id')
    pre_date = request.args.get('pre_date', '')
    pre_format = request.args.get('pre_format', '')
    pre_rewatch = request.args.get('pre_rewatch', 'false')
    
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        replace_id = request.form.get('replace_id')
    
    normalized_results = []
    if query:
        raw_results = GoogleBooksService.search_books(query)
        is_google = True
        
        if raw_results == "RATE_LIMIT":
            raw_results = OpenLibraryService.search_books(query)
            is_google = False
        
        for book in raw_results:
            if is_google:
                info = book.get('volumeInfo', {})
                normalized_results.append({
                    'id': book.get('id'),
                    'title': info.get('title'),
                    'author': ", ".join(info.get('authors', [])) if info.get('authors') else 'Unknown',
                    'year': info.get('publishedDate', '')[:4],
                    'description': info.get('description', ''),
                    'thumbnail': info.get('imageLinks', {}).get('thumbnail', '').replace('http://', 'https://'),
                    'source': 'google'
                })
            else:
                normalized_results.append({
                    'id': book.get('key', '').split('/')[-1],
                    'title': book.get('title'),
                    'author': book.get('author_name', ['Unknown'])[0],
                    'year': book.get('first_publish_year', ''),
                    'description': f"Edition count: {book.get('edition_count', 0)}",
                    'thumbnail': f"https://covers.openlibrary.org/b/id/{book.get('cover_i')}-M.jpg" if book.get('cover_i') else None,
                    'source': 'openlibrary'
                })
        
    return render_template('book_search.html', 
                         results=normalized_results, 
                         query=query, 
                         replace_id=replace_id,
                         pre_date=pre_date,
                         pre_format=pre_format,
                         pre_rewatch=pre_rewatch)

@main.route('/books/add/<book_id>', methods=['POST'])
@login_required
def add_book(book_id):
    replace_id = request.form.get('replace_id')
    source = request.form.get('source', 'google')
    
    title, author, summary, page_count, genres, release_year, cover_filename = None, None, None, None, None, None, None

    if source == 'google':
        details = GoogleBooksService.get_book_details(book_id)
        if details:
            volume_info = details.get('volumeInfo', {})
            title = volume_info.get('title')
            author = ", ".join(volume_info.get('authors', [])) if volume_info.get('authors') else 'Unknown'
            summary = volume_info.get('description', '')
            page_count = volume_info.get('pageCount')
            genres = ", ".join(volume_info.get('categories', [])) if volume_info.get('categories') else ''
            release_year = int(volume_info.get('publishedDate', '0')[:4]) if volume_info.get('publishedDate') else None
            
            image_links = volume_info.get('imageLinks', {})
            image_url = image_links.get('extraLarge') or image_links.get('large') or image_links.get('medium') or image_links.get('thumbnail')
            if image_url:
                cover_filename = GoogleBooksService.download_cover(image_url, book_id)
    else: # openlibrary
        details = OpenLibraryService.get_book_details(book_id)
        if details:
            title = details.get('title')
            author = 'Unknown' 
            desc = details.get('description', '')
            summary = desc.get('value', '') if isinstance(desc, dict) else desc
            genres = ", ".join(details.get('subjects', [])[:5]) if details.get('subjects') else ''
            covers = details.get('covers', [])
            if covers:
                cover_filename = OpenLibraryService.download_book_cover(cover_id=covers[0])
            else:
                cover_filename = OpenLibraryService.download_book_cover(ol_id=book_id)

    if not title:
        flash(f"Error fetching book details from {source.capitalize()}.")
        return redirect(url_for('main.search_book'))

    date_finished_str = request.form.get('date_finished')
    book_format = request.form.get('format')
    is_rewatch = True if request.form.get('is_rewatch') == 'on' else False
    rating = request.form.get('rating', type=float)
    
    try:
        date_finished = datetime.strptime(date_finished_str, '%Y-%m-%d').date() if date_finished_str else datetime.now().date()
    except ValueError:
        date_finished = datetime.now().date()

    if replace_id:
        book = Book.query.get_or_404(replace_id)
        book.title = title
        book.author = author
        book.external_id = book_id
        book.summary = summary
        book.poster_path = cover_filename
        book.page_count = page_count
        book.genres = genres
        book.release_year = release_year
        
        if date_finished_str:
            book.date_finished = date_finished
        if book_format:
            book.format = book_format
        if request.form.get('is_rewatch'):
            book.is_revisit = is_rewatch
        if rating:
            book.storygraph_rating = rating
            
        flash(f"Refreshed details for {book.title}!")
    else:
        new_book = Book(
            title=title,
            author=author,
            external_id=book_id,
            summary=summary,
            poster_path=cover_filename,
            page_count=page_count,
            genres=genres,
            release_year=release_year,
            format=book_format,
            is_revisit=is_rewatch,
            date_finished=date_finished,
            storygraph_rating=rating
        )
        db.session.add(new_book)
        flash(f"Added {new_book.title} to your tracker!")
    
    db.session.commit()
    return redirect(url_for('main.books_list'))

@main.route('/books/edit/<int:book_id>', methods=['POST'])
@login_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    date_str = request.form.get('date_finished')
    if date_str:
        try:
            book.date_finished = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format.")
            return redirect(url_for('main.books_list'))

    book.format = request.form.get('format')
    book.storygraph_rating = request.form.get('rating', type=float)
    book.is_revisit = True if request.form.get('is_rewatch') == 'on' else False
    
    db.session.commit()
    flash(f"Updated tracking for {book.title}.")
    return redirect(url_for('main.books_list'))

@main.route('/books/delete/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    title = book.title
    db.session.delete(book)
    db.session.commit()
    flash(f"Removed {title} from your tracker.")
    return redirect(url_for('main.books_list'))

# THEATER ROUTES
@main.route('/theater')
def theater_list():
    all_shows = Theater.query.order_by(Theater.date_watched.asc()).all()
    grouped = OrderedDict()
    for show in all_shows:
        year = show.date_watched.year if show.date_watched else "Unknown"
        if year not in grouped:
            grouped[year] = []
        grouped[year].append(show)
    return render_template('theater.html', grouped_shows=grouped, total_count=len(all_shows), now=datetime.now())

@main.route('/theater/search', methods=['GET', 'POST'])
@login_required
def search_theater():
    online_results = []
    query = request.args.get('query', '')
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
    
    if query:
        # Search IBDB exclusively
        online_results = IBDBService.search_shows(query)
        
    return render_template('theater_search.html', online_results=online_results, query=query)

@main.route('/theater/add-ibdb/<string:slug_id>', methods=['POST'])
@login_required
def add_theater_ibdb(slug_id):
    title = request.form.get('title')
    show_type = request.form.get('show_type')
    date_watched_str = request.form.get('date_watched')
    location = request.form.get('location')
    is_rewatch = True if request.form.get('is_rewatch') == 'on' else False
    selected_image = request.form.get('poster_url')
    
    # Fetch extra details from IBDB
    details = IBDBService.get_show_details(slug_id)
    opening_date_str = details.get('opening_date')
    original_theater = details.get('theater')
    summary = details.get('summary')
    
    try:
        date_watched = datetime.strptime(date_watched_str, '%Y-%m-%d').date() if date_watched_str else datetime.now().date()
    except ValueError:
        date_watched = datetime.now().date()

    release_year = None
    if opening_date_str:
        # IBDB date format varies, but usually Month Day, Year
        try:
            # Handle "Aug 6, 2015"
            release_year = int(opening_date_str.split(',')[-1].strip())
        except: pass

    # Download selected poster if provided
    poster_filename = None
    if selected_image:
        poster_filename = ImageSearchService.download_image(selected_image, 'theater', slug_id.split('-')[-1])

    new_show = Theater(
        title=title,
        date_watched=date_watched,
        location=location,
        is_revisit=is_rewatch,
        release_year=release_year,
        original_theater=original_theater,
        show_type=show_type,
        poster_path=poster_filename,
        summary=summary
    )
    db.session.add(new_show)
    db.session.commit()
    flash(f"Added {new_show.title} (via IBDB) to your tracker!")
    return redirect(url_for('main.theater_list'))

@main.route('/theater/get-posters')
@login_required
def get_theater_posters():
    query = request.args.get('query')
    if not query:
        return {"images": []}
    images = WikipediaService.search_posters(query)
    return {"images": images}

@main.route('/theater/delete/<int:show_id>', methods=['POST'])
@login_required
def delete_theater(show_id):
    show = Theater.query.get_or_404(show_id)
    title = show.title
    db.session.delete(show)
    db.session.commit()
    flash(f"Removed {title} from your tracker.")
    return redirect(url_for('main.theater_list'))

@main.route('/backfill-theater')
@login_required
def trigger_backfill_theater():
    from app.backfill_theater import run_backfill_theater
    try:
        count = run_backfill_theater()
        flash(f"Successfully backfilled {count} theater shows!")
    except Exception as e:
        flash(f"Error during theater backfill: {str(e)}")
    return redirect(url_for('main.theater_list'))

@main.route('/backfill-games')
def trigger_backfill_games():
    from app.backfill_games import run_backfill_games
    try:
        count = run_backfill_games()
        flash(f"Successfully backfilled {count} games!")
    except Exception as e:
        flash(f"Error during game backfill: {str(e)}")
    return redirect(url_for('main.games_list'))

@main.route('/backfill-books')
def trigger_backfill_books():
    from app.backfill_books import run_backfill_books
    try:
        count = run_backfill_books()
        flash(f"Successfully backfilled {count} books!")
    except Exception as e:
        flash(f"Error during book backfill: {str(e)}")
    return redirect(url_for('main.books_list'))
