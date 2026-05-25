from app import create_app, db
from app.models import Movie
from app.services import TMDBService
import time

app = create_app()

def scrape_posters():
    with app.app_context():
        movies = Movie.query.all()
        print(f"Starting poster scrape for {len(movies)} movies...")
        
        count = 0
        for movie in movies:
            if movie.poster_path:
                print(f"Downloading poster for: {movie.title}...")
                success = TMDBService.download_poster(movie.poster_path)
                if success:
                    count += 1
                else:
                    print(f"  Failed to download poster for {movie.title}")
                
                # Small sleep to be nice to TMDB API
                if count % 10 == 0:
                    time.sleep(1)
        
        print(f"Finished! Downloaded {count} posters.")

if __name__ == '__main__':
    scrape_posters()