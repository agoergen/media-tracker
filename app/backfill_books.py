import csv
from datetime import datetime
from app import db
from app.models import Book

def run_backfill_books():
    csv_path = 'app/backfill_data/books.csv' # I will create this dir and file
    count = 0
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get('Title')
            if not title:
                continue
                
            # Date parsing (M/D/YYYY)
            date_finished = None
            date_str = row.get('Date Finished')
            if date_str:
                try:
                    date_finished = datetime.strptime(date_str, '%m/%d/%Y').date()
                except ValueError:
                    pass
            
            # Rating
            rating = None
            rating_str = row.get('Goodreads Rating') # Keeping CSV header but mapping to StoryGraph
            if rating_str:
                try:
                    rating = float(rating_str)
                except ValueError:
                    pass

            # Reread
            is_reread = row.get('Reread') == 'X'
            
            # Check if exists
            existing = Book.query.filter_by(title=title, author=row.get('Author')).first()
            if not existing:
                book = Book(
                    title=title,
                    author=row.get('Author'),
                    format=row.get('Format'),
                    date_finished=date_finished,
                    release_year=int(row.get('Year Published')) if row.get('Year Published') and row.get('Year Published').isdigit() else None,
                    storygraph_rating=rating,
                    is_revisit=is_reread
                )
                db.session.add(book)
                count += 1
                
    db.session.commit()
    return count
