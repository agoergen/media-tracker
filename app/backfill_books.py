import csv
import time
from datetime import datetime
from app import db
from app.models import Book
from app.services import GoogleBooksService

def run_backfill_books():
    csv_path = 'app/backfill_data/books.csv'
    count = 0
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get('Title')
            author_csv = row.get('Author')
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
            rating_str = row.get('Goodreads Rating')
            if rating_str:
                try:
                    rating = float(rating_str)
                except ValueError:
                    pass

            # Reread
            is_reread = row.get('Reread') == 'X'
            
            # Check if exists (check for existing by title/author)
            book = Book.query.filter_by(title=title, author=author_csv).first()
            
            if not book:
                book = Book(
                    title=title,
                    author=author_csv,
                    format=row.get('Format'),
                    date_finished=date_finished,
                    release_year=int(row.get('Year Published')) if row.get('Year Published') and row.get('Year Published').isdigit() else None,
                    storygraph_rating=rating,
                    is_revisit=is_reread
                )
                db.session.add(book)
                count += 1
            
            # Enrich with Google Books
            print(f"Enriching with Google Books: {title} by {author_csv}...")
            search_query = f"intitle:{title}"
            if author_csv:
                search_query += f"+inauthor:{author_csv}"
            
            results = GoogleBooksService.search_books(search_query)
            
            if results:
                match = results[0]
                volume_id = match.get('id')
                volume_info = match.get('volumeInfo', {})
                
                if volume_id:
                    book.external_id = volume_id
                    book.summary = volume_info.get('description', book.summary)
                    book.page_count = volume_info.get('pageCount', book.page_count)
                    book.genres = ", ".join(volume_info.get('categories', [])) if volume_info.get('categories') else book.genres
                    book.google_books_url = volume_info.get('canonicalVolumeLink') or volume_info.get('infoLink')
                    
                    # Cover
                    image_links = volume_info.get('imageLinks', {})
                    image_url = image_links.get('extraLarge') or image_links.get('large') or image_links.get('medium') or image_links.get('thumbnail')
                    if image_url:
                        book.poster_path = GoogleBooksService.download_cover(image_url, volume_id)
            
            # Small sleep to be polite
            time.sleep(0.2)

    db.session.commit()
    return count
