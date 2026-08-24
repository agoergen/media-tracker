import os
import sys
import zipfile
import argparse
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from config import Config
from app import create_app, db
from app.models import Movie, TVSeason, Game, Book, Theater, FutureMediaGoal, BacklogItem
from app.services import TMDBService, IGDBService, GoogleBooksService, OpenLibraryService, IBDBService, ImageSearchService

def get_upload_folder():
    folder = Config.UPLOAD_FOLDER
    os.makedirs(folder, exist_ok=True)
    return folder

def get_backup_dir():
    basedir = os.path.abspath(os.path.dirname(__file__))
    backup_dir = os.path.join(basedir, 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir

def export_zip():
    folder = get_upload_folder()
    backup_dir = get_backup_dir()
    
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    if not files:
        print(f"No posters found in {folder} to export.")
        return

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_path = os.path.join(backup_dir, f"posters_backup_{timestamp}.zip")
    
    print(f"Archiving {len(files)} posters from {folder}...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for f in files:
            file_path = os.path.join(folder, f)
            zipf.write(file_path, arcname=f)
            
    size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"\nExport complete! Saved to: {os.path.relpath(zip_path)} ({size_mb:.2f} MB)")

def select_zip_file():
    backup_dir = get_backup_dir()
    files = [f for f in os.listdir(backup_dir) if f.startswith('posters_backup_') and f.endswith('.zip')]
    if not files:
        print("No posters_backup_*.zip files found in ./backups directory.")
        return None
        
    files.sort(key=lambda f: os.path.getmtime(os.path.join(backup_dir, f)), reverse=True)
    
    print("\nSelect a poster ZIP backup to restore:")
    print("---------------------------------------")
    for idx, f in enumerate(files, 1):
        full_path = os.path.join(backup_dir, f)
        size_mb = os.path.getsize(full_path) / (1024 * 1024)
        mtime = datetime.fromtimestamp(os.path.getmtime(full_path)).strftime('%Y-%m-%d %H:%M:%S')
        tag = " [Latest]" if idx == 1 else ""
        print(f"{idx}. {f} ({size_mb:.2f} MB - {mtime}){tag}")
    print(f"{len(files)+1}. Enter custom file path")
    
    choice = input(f"\nEnter choice (1-{len(files)+1}): ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(files):
        return os.path.join(backup_dir, files[int(choice)-1])
    elif choice == str(len(files)+1):
        custom = input("Enter path to ZIP file: ").strip()
        return custom if custom else None
    else:
        print("Defaulting to latest archive.")
        return os.path.join(backup_dir, files[0])

def import_zip(zip_path=None):
    if not zip_path:
        zip_path = select_zip_file()
        if not zip_path:
            print("No ZIP file selected. Exiting.")
            return

    if not os.path.exists(zip_path):
        print(f"ZIP file not found: {zip_path}")
        return

    folder = get_upload_folder()
    print(f"\nExtracting posters from '{os.path.relpath(zip_path)}' into {folder}...")
    
    count = 0
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        file_list = zipf.namelist()
        for member in file_list:
            # Prevent directory traversal
            if member.startswith('/') or '..' in member:
                continue
            zipf.extract(member, folder)
            count += 1

    print(f"\nImport complete! Extracted {count} poster files to {folder}.")

def get_all_poster_filenames_from_db(db_url=None):
    if db_url:
        Config.SQLALCHEMY_DATABASE_URI = db_url
    app = create_app(Config)
    
    filenames = set()
    with app.app_context():
        models = [Movie, TVSeason, Game, Book, Theater, FutureMediaGoal, BacklogItem]
        for model in models:
            try:
                for row in model.query.all():
                    p = getattr(row, 'poster_path', None)
                    if p:
                        # Extract basename in case a relative path is stored
                        filenames.add(os.path.basename(p))
            except Exception as e:
                print(f"Error querying {model.__name__}: {e}")
                
    return sorted(list(filenames))

def download_from_url():
    folder = get_upload_folder()
    
    print("\nDownload Posters from an Application URL (Out-of-band)")
    print("-----------------------------------------------------")
    default_url = os.environ.get('PRODUCTION_APP_URL', 'https://leisureledger.up.railway.app')
    url_input = input(f"Enter Application Base URL [{default_url}]: ").strip()
    base_url = url_input if url_input else default_url
    base_url = base_url.rstrip('/')

    db_url = input("Enter Database URL to inspect poster list (Leave blank for current .env DB): ").strip()
    
    print("\nRetrieving required poster filenames from database...")
    required_files = get_all_poster_filenames_from_db(db_url if db_url else None)
    print(f"Found {len(required_files)} unique posters referenced in database.")

    if not required_files:
        print("No posters referenced in database.")
        return

    downloaded = 0
    skipped = 0
    failed = 0

    print(f"\nDownloading missing posters into {folder}...")
    for idx, fname in enumerate(required_files, 1):
        target_path = os.path.join(folder, fname)
        if os.path.exists(target_path) and os.path.getsize(target_path) > 0:
            skipped += 1
            continue

        poster_url = f"{base_url}/posters/{fname}"
        try:
            resp = requests.get(poster_url, timeout=10)
            if resp.status_code == 200 and resp.content:
                with open(target_path, 'wb') as f:
                    f.write(resp.content)
                downloaded += 1
                print(f"  [{idx}/{len(required_files)}] Downloaded: {fname}")
            else:
                failed += 1
                print(f"  [{idx}/{len(required_files)}] Failed ({resp.status_code}): {fname}")
        except Exception as e:
            failed += 1
            print(f"  [{idx}/{len(required_files)}] Error downloading {fname}: {e}")

    print(f"\nDownload Summary: {downloaded} downloaded, {skipped} already existed, {failed} failed.")

def refetch_from_apis():
    folder = get_upload_folder()
    
    print("\nDownload/Re-fetch Posters from Source APIs (Air-Gapped)")
    print("-----------------------------------------------------")
    db_url = input("Enter Database URL (Leave blank for current .env DB): ").strip()
    if db_url:
        Config.SQLALCHEMY_DATABASE_URI = db_url
    
    app = create_app(Config)
    with app.app_context():
        print("\nScanning database for missing posters...")
        
        # 1. Movies
        movies = Movie.query.all()
        for m in movies:
            target = os.path.join(folder, m.poster_path) if m.poster_path else None
            if not target or not os.path.exists(target) or os.path.getsize(target) == 0:
                if m.external_id:
                    print(f"Re-fetching Movie poster: {m.title}...")
                    details = TMDBService.get_movie_details(m.external_id)
                    if details and details.get('poster_path'):
                        fname = TMDBService.download_and_save_poster(details['poster_path'], m.external_id)
                        if fname:
                            m.poster_path = fname

        # 2. TV
        seasons = TVSeason.query.all()
        for s in seasons:
            target = os.path.join(folder, s.poster_path) if s.poster_path else None
            if not target or not os.path.exists(target) or os.path.getsize(target) == 0:
                if s.external_id:
                    print(f"Re-fetching TV Season poster: {s.series_title} S{s.season_number}...")
                    details = TMDBService.get_tv_details(s.external_id, s.season_number or 1)
                    if details and details.get('poster_path'):
                        fname = TMDBService.download_and_save_poster(details['poster_path'], f"{s.external_id}_s{s.season_number}")
                        if fname:
                            s.poster_path = fname

        # 3. Games
        games = Game.query.all()
        for g in games:
            target = os.path.join(folder, g.poster_path) if g.poster_path else None
            if not target or not os.path.exists(target) or os.path.getsize(target) == 0:
                if g.external_id:
                    print(f"Re-fetching Game cover: {g.title}...")
                    details = IGDBService.get_game_details(g.external_id)
                    if details and details.get('cover', {}).get('image_id'):
                        fname = IGDBService.download_and_save_cover(details['cover']['image_id'], g.external_id)
                        if fname:
                            g.poster_path = fname

        # 4. Books
        books = Book.query.all()
        for b in books:
            target = os.path.join(folder, b.poster_path) if b.poster_path else None
            if not target or not os.path.exists(target) or os.path.getsize(target) == 0:
                if b.external_id:
                    print(f"Re-fetching Book cover: {b.title}...")
                    details = GoogleBooksService.get_book_details(b.external_id)
                    img_url = details.get('image_url') if details else None
                    if not img_url:
                        ol_details = OpenLibraryService.get_book_details(b.external_id)
                        img_url = ol_details.get('image_url') if ol_details else None
                    if img_url:
                        fname = GoogleBooksService.download_and_save_cover(img_url, b.external_id)
                        if fname:
                            b.poster_path = fname

        db.session.commit()
        print("\nRe-fetch complete! Database poster references updated.")

def main_menu():
    print("==================================================")
    print("      LeisureLedger Volume Maintenance Utility    ")
    print("==================================================")
    print("1. Export posters directory to a ZIP backup")
    print("2. Import posters from a ZIP backup file")
    print("3. Download posters from Application URL (Out-of-band mirror)")
    print("4. Download/Re-fetch posters directly from Source APIs")
    print("5. Exit")
    
    choice = input("\nEnter choice (1-5): ").strip()
    if choice == '1':
        export_zip()
    elif choice == '2':
        import_zip()
    elif choice == '3':
        download_from_url()
    elif choice == '4':
        refetch_from_apis()
    elif choice == '5':
        print("Exiting.")
        return
    else:
        print("Invalid selection.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="LeisureLedger Volume Maintenance Utility")
    parser.add_argument('--export', action='store_true', help="Export posters to ZIP archive")
    parser.add_argument('--import-zip', nargs='?', const='interactive', type=str, help="Import posters from ZIP archive")
    parser.add_argument('--download-url', action='store_true', help="Download posters from an application URL")
    parser.add_argument('--refetch-apis', action='store_true', help="Re-fetch missing posters from third-party APIs")
    args = parser.parse_args()

    if args.export:
        export_zip()
    elif args.import_zip:
        if args.import_zip == 'interactive':
            import_zip()
        else:
            import_zip(args.import_zip)
    elif args.download_url:
        download_from_url()
    elif args.refetch_apis:
        refetch_from_apis()
    else:
        main_menu()
