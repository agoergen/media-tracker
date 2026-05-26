import csv
from datetime import datetime
from app import db
from app.models import Theater

def run_backfill_theater():
    csv_path = 'app/backfill_data/theater.csv'
    count = 0
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get('Production Title', '').strip()
            if not title:
                continue
                
            # Date parsing (M/D/YY or M/D/YYYY)
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
            
            # Check if exists to avoid duplicates on re-run
            existing = Theater.query.filter_by(title=title, date_watched=date_watched).first()
            if not existing:
                show = Theater(
                    title=title,
                    location=row.get('Location'),
                    date_watched=date_watched,
                    release_year=int(row.get('Original Year of Release')) if row.get('Original Year of Release') and row.get('Original Year of Release').isdigit() else None,
                    is_revisit=False
                )
                db.session.add(show)
                count += 1
                
    db.session.commit()
    return count
