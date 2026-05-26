import csv
import time
from datetime import datetime
from app import db
from app.models import Theater, TheaterReference
from app.services import WikipediaService, ImageSearchService

def run_backfill_theater():
    csv_path = 'app/backfill_data/theater.csv'
    count = 0
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get('Production Title', '').strip()
            if not title:
                continue
                
            # Date parsing (M/D/YY)
            date_watched = None
            date_str = row.get('Date Watched')
            if date_str:
                try:
                    if len(date_str.split('/')[-1]) == 2:
                        date_watched = datetime.strptime(date_str, '%m/%d/%y').date()
                    else:
                        date_watched = datetime.strptime(date_str, '%m/%d/%Y').date()
                except ValueError:
                    pass
            
            # Check if exists
            show = Theater.query.filter_by(title=title, date_watched=date_watched).first()
            if not show:
                # Try to find reference info
                ref = TheaterReference.query.filter(TheaterReference.show_name.ilike(title)).first()
                
                show = Theater(
                    title=title,
                    location=row.get('Location'),
                    date_watched=date_watched,
                    release_year=int(row.get('Original Year of Release')) if row.get('Original Year of Release') and row.get('Original Year of Release').isdigit() else None,
                    is_revisit=False
                )
                
                if ref:
                    show.original_theater = ref.theatre
                    show.run_time = ref.run_time_minutes
                    show.show_type = ref.show_type
                    if not show.release_year and ref.date_open:
                        try:
                            show.release_year = int(ref.date_open[:4])
                        except:
                            pass
                
                db.session.add(show)
                db.session.flush() # Get ID for image download
                count += 1

            # Enrich with Wikipedia Poster if missing
            if not show.poster_path:
                print(f"Fetching poster for {title}...")
                posters = WikipediaService.search_posters(title)
                if posters:
                    # Just take the first one for backfill
                    show.poster_path = ImageSearchService.download_image(posters[0], 'theater', show.id)
                time.sleep(0.5)
                
    db.session.commit()
    return count
