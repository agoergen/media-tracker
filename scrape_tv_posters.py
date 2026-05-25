from app import create_app, db
from app.models import TVSeason
from app.services import TMDBService
import time

app = create_app()

def scrape_tv_posters():
    with app.app_context():
        seasons = TVSeason.query.all()
        print(f"Starting poster scrape for {len(seasons)} TV seasons...")
        
        count = 0
        for season in seasons:
            if season.poster_path:
                print(f"Downloading poster for: {season.series_title} S{season.season_number}...")
                success = TMDBService.download_poster(season.poster_path)
                if success:
                    count += 1
                else:
                    print(f"  Failed to download poster for {season.series_title} S{season.season_number}")
                
                # Small sleep to be nice to TMDB API
                if count % 10 == 0:
                    time.sleep(1)
        
        print(f"Finished! Downloaded {count} TV posters.")

if __name__ == '__main__':
    scrape_tv_posters()