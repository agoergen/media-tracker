import csv
import time
from datetime import datetime
from app import db
from app.models import Book
from app.services import OpenLibraryService

def run_backfill_books():
    csv_path = 'app/backfill_data/books.csv'
    count = 0
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get('Title')
            author = row.get('Author')
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
            book = Book.query.filter_by(title=title, author=author).first()
            
            if not book:
                book = Book(
                    title=title,
                    author=author,
                    format=row.get('Format'),
                    date_finished=date_finished,
                    release_year=int(row.get('Year Published')) if row.get('Year Published') and row.get('Year Published').isdigit() else None,
                    storygraph_rating=rating,
                    is_revisit=is_reread
                )
                db.session.add(book)
                count += 1
            
            # Enforce metadata/cover fetch if not present
            if not book.external_id or not book.poster_path:
                print(f"Enriching: {title} by {author}...")
                search_query = f"{title} {author}" if author else title
                results = OpenLibraryService.search_books(search_query)
                
                if results:
                    # Match by title as closely as possible from results
                    match = results[0] # Take first result for now
                    ol_id = match.get('key', '').split('/')[-1]
                    
                    if ol_id:
                        book.external_id = ol_id
                        
                        # Get full details for summary/page count
                        details = OpenLibraryService.get_book_details(ol_id)
                        if details:
                            # Summary
                            desc = details.get('description', '')
                            if isinstance(desc, dict):
                                desc = desc.get('value', '')
                            book.summary = desc
                            
                            # Page count (usually in edition, but OL API is tricky)
                            # OpenLibrary search results often have 'number_of_pages_median'
                            book.page_count = match.get('number_of_pages_median')
                            
                            # Genres
                            subjects = details.get('subjects', [])
                            if subjects:
                                book.genres = ", ".join(subjects[:5])
                        
                        # Cover
                        cover_id = match.get('cover_i')
                        if cover_id:
                            book.poster_path = OpenLibraryService.download_book_cover(cover_id=cover_id)
                        else:
                            # Try fallback by OLID
                            book.poster_path = OpenLibraryService.download_book_cover(ol_id=ol_id)
                
                # Small sleep to be polite to OpenLibrary API
                time.sleep(0.5)

    db.session.commit()
    return count
