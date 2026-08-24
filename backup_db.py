import os
import json
import argparse
from datetime import datetime, date as pydate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app import create_app, db
from app.models import User, Movie, TVSeason, Game, Book, Theater, Goal, FutureMediaGoal, BacklogItem

def save_production_url(url):
    env_path = '.env'
    lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    
    # Update or append
    updated = False
    new_lines = []
    for line in lines:
        if line.strip().startswith('PRODUCTION_DATABASE_URL='):
            new_lines.append(f"PRODUCTION_DATABASE_URL={url}\n")
            updated = True
        else:
            new_lines.append(line)
            
    if not updated:
        # Make sure there is a newline at the end if the file is not empty
        if new_lines and not new_lines[-1].endswith('\n'):
            new_lines[-1] += '\n'
        new_lines.append(f"PRODUCTION_DATABASE_URL={url}\n")
        
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Saved production URL to .env file as PRODUCTION_DATABASE_URL.")

def generate_sql_insert(models):
    sql_lines = [
        "-- LeisureLedger SQL Backup",
        f"-- Generated at: {datetime.now().isoformat()}",
        "--",
        ""
    ]
    for name, model in models.items():
        sql_lines.append(f"-- Table: {model.__table__.name}")
        try:
            rows = model.query.all()
            for row in rows:
                cols = []
                vals = []
                for col in row.__table__.columns:
                    val = getattr(row, col.name)
                    cols.append(col.name)
                    if val is None:
                        vals.append("NULL")
                    elif isinstance(val, bool):
                        vals.append("TRUE" if val else "FALSE")
                    elif isinstance(val, (int, float)):
                        vals.append(str(val))
                    else:
                        # Escape single quotes for SQL insertion
                        escaped = str(val).replace("'", "''")
                        vals.append(f"'{escaped}'")
                
                cols_str = ", ".join(cols)
                vals_str = ", ".join(vals)
                sql_lines.append(f"INSERT INTO {model.__table__.name} ({cols_str}) VALUES ({vals_str});")
            sql_lines.append("")
        except Exception as e:
            sql_lines.append(f"-- Failed to backup data for {name}: {e}")
            sql_lines.append("")
    return "\n".join(sql_lines)

def select_database(action_name):
    env_db_url = os.environ.get('DATABASE_URL')
    prod_db_url = os.environ.get('PRODUCTION_DATABASE_URL')
    
    print(f"LeisureLedger Database {action_name} Utility")
    print("-----------------------------------")
    print("Select database option:")
    print("1. Enter a custom database connection string (e.g. Railway production URL)")
    print("2. Local SQLite database (app.db)")
    
    options = {}
    opt_index = 3
    
    if env_db_url:
        display_env = env_db_url.split('@')[-1] if '@' in env_db_url else env_db_url
        print(f"{opt_index}. Configured database from .env ({display_env})")
        options[str(opt_index)] = env_db_url
        opt_index += 1
        
    if prod_db_url:
        display_prod = prod_db_url.split('@')[-1] if '@' in prod_db_url else prod_db_url
        print(f"{opt_index}. Saved Production Database from .env ({display_prod})")
        options[str(opt_index)] = prod_db_url
        opt_index += 1
        
    choice = input(f"\nEnter choice (1-{opt_index-1}): ").strip()
    
    db_url = ""
    is_custom = False
    
    if choice == '1':
        db_url = input("Enter connection string (e.g., postgresql://...): ").strip()
        is_custom = True
    elif choice == '2':
        basedir = os.path.abspath(os.path.dirname(__file__))
        db_url = 'sqlite:///' + os.path.join(basedir, 'app.db')
    elif choice in options:
        db_url = options[choice]
    else:
        # Default fallbacks
        if prod_db_url:
            print("Using saved production database.")
            db_url = prod_db_url
        elif env_db_url:
            print("Using database configured in .env.")
            db_url = env_db_url
        else:
            print("Using local SQLite database.")
            basedir = os.path.abspath(os.path.dirname(__file__))
            db_url = 'sqlite:///' + os.path.join(basedir, 'app.db')
            
    return db_url, is_custom

def backup():
    db_url, is_custom = select_database("Backup")
    
    if not db_url:
        print("No database URL provided. Exiting.")
        return

    # Temporarily override database config
    from config import Config
    Config.SQLALCHEMY_DATABASE_URI = db_url
    app = create_app(Config)

    with app.app_context():
        display_url = db_url.split('@')[-1] if '@' in db_url else db_url
        print(f"\nConnecting to database: {display_url}...")
        try:
            # Check connection
            db.engine.connect()
        except Exception as e:
            print(f"Failed to connect to database: {e}")
            return

        # If custom connection worked, offer to save it
        if is_custom:
            save_choice = input("Would you like to save this connection string in your .env file as PRODUCTION_DATABASE_URL for future use? (y/n): ").strip().lower()
            if save_choice == 'y':
                save_production_url(db_url)

        # Make sure backups folder exists
        basedir = os.path.abspath(os.path.dirname(__file__))
        backup_dir = os.path.join(basedir, 'backups')
        os.makedirs(backup_dir, exist_ok=True)

        backup_data = {}

        # List of models to back up
        models = {
            'User': User,
            'Movie': Movie,
            'TVSeason': TVSeason,
            'Game': Game,
            'Book': Book,
            'Theater': Theater,
            'Goal': Goal,
            'FutureMediaGoal': FutureMediaGoal,
            'BacklogItem': BacklogItem
        }

        for name, model in models.items():
            print(f"Backing up {name} table...")
            try:
                rows = model.query.all()
                table_data = []
                for row in rows:
                    row_dict = {}
                    for col in row.__table__.columns:
                        val = getattr(row, col.name)
                        # Convert dates/datetimes to ISO strings for JSON serialization
                        if hasattr(val, 'isoformat'):
                            val = val.isoformat()
                        row_dict[col.name] = val
                    table_data.append(row_dict)
                backup_data[name] = table_data
            except Exception as e:
                print(f"Failed to back up table {name}: {e}")

        # Set output filenames
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_filename = os.path.join(backup_dir, f"leisureledger_backup_{timestamp}.json")
        sql_filename = os.path.join(backup_dir, f"leisureledger_backup_{timestamp}.sql")
        
        # Write JSON file
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        print(f"JSON backup saved to: {os.path.relpath(json_filename, basedir)}")

        # Write SQL file
        sql_content = generate_sql_insert(models)
        with open(sql_filename, 'w', encoding='utf-8') as f:
            f.write(sql_content)
        print(f"SQL backup saved to: {os.path.relpath(sql_filename, basedir)}")
            
        print("\nBackup completed successfully!")

def select_backup_file():
    basedir = os.path.abspath(os.path.dirname(__file__))
    backup_dir = os.path.join(basedir, 'backups')
    if not os.path.exists(backup_dir):
        print("No backups directory found.")
        return None
    
    files = [f for f in os.listdir(backup_dir) if f.endswith('.json')]
    if not files:
        print("No .json backup files found in ./backups directory.")
        return None
    
    # Sort files by modified time descending (newest first)
    files.sort(key=lambda f: os.path.getmtime(os.path.join(backup_dir, f)), reverse=True)
    
    print("\nSelect a backup file to restore:")
    print("-----------------------------------")
    for idx, f in enumerate(files, 1):
        full_path = os.path.join(backup_dir, f)
        size_kb = os.path.getsize(full_path) / 1024
        mtime = datetime.fromtimestamp(os.path.getmtime(full_path)).strftime('%Y-%m-%d %H:%M:%S')
        tag = " [Latest]" if idx == 1 else ""
        print(f"{idx}. {f} ({size_kb:.1f} KB - {mtime}){tag}")
    print(f"{len(files)+1}. Enter custom file path")
    
    choice = input(f"\nEnter choice (1-{len(files)+1}): ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(files):
        return os.path.join(backup_dir, files[int(choice)-1])
    elif choice == str(len(files)+1):
        custom = input("Enter path to backup .json file: ").strip()
        return custom if custom else None
    else:
        print("Defaulting to latest backup.")
        return os.path.join(backup_dir, files[0])

def restore(filename=None):
    if not filename:
        filename = select_backup_file()
        if not filename:
            print("No backup file selected. Exiting.")
            return

    if not os.path.exists(filename):
        print(f"Backup file not found: {filename}")
        return

    # Check if backup file is JSON
    if not filename.endswith('.json'):
        print("Error: The restore function only supports JSON backup files.")
        return

    db_url, _ = select_database("Restore")

    if not db_url:
        print("No database URL provided. Exiting.")
        return

    from config import Config
    Config.SQLALCHEMY_DATABASE_URI = db_url
    app = create_app(Config)

    with open(filename, 'r', encoding='utf-8') as f:
        backup_data = json.load(f)

    with app.app_context():
        display_url = db_url.split('@')[-1] if '@' in db_url else db_url
        print(f"\nWARNING: You are about to restore data from '{filename}' into database: {display_url}")
        confirm = input("This will overwrite/insert data. Proceed? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Restore canceled.")
            return

        # Clear existing tables first?
        clear_existing = input("Clear existing tables before restoring? (y/n): ").strip().lower() == 'y'

        models = {
            'User': User,
            'Movie': Movie,
            'TVSeason': TVSeason,
            'Game': Game,
            'Book': Book,
            'Theater': Theater,
            'Goal': Goal,
            'FutureMediaGoal': FutureMediaGoal,
            'BacklogItem': BacklogItem
        }

        try:
            import sqlalchemy as sa
            
            for name, model in models.items():
                if name not in backup_data:
                    continue

                if clear_existing:
                    print(f"Clearing existing data in {name} table...")
                    model.query.delete()

                print(f"Restoring {name} table ({len(backup_data[name])} rows)...")
                for row_dict in backup_data[name]:
                    inst = model()
                    for col in model.__table__.columns:
                        val = row_dict.get(col.name)
                        if val is not None:
                            # Convert back to date/datetime objects if columns are date/datetime
                            if isinstance(col.type, sa.Date):
                                val = pydate.fromisoformat(val)
                            elif isinstance(col.type, sa.DateTime):
                                val = datetime.fromisoformat(val)
                        setattr(inst, col.name, val)
                    db.session.add(inst)
            
            db.session.commit()
            print("\nRestore completed successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error during restore: {e}")

def main_menu():
    print("==================================================")
    print("        LeisureLedger Database Utility            ")
    print("==================================================")
    print("1. Create a new database backup")
    print("2. Restore database from a backup")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    if choice == '1':
        backup()
    elif choice == '2':
        restore()
    elif choice == '3':
        print("Exiting.")
        return
    else:
        print("Invalid selection. Defaulting to backup.")
        backup()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="LeisureLedger Database Backup Utility")
    parser.add_argument('--restore', nargs='?', const='interactive', type=str, help="Restore mode. Optionally provide path to JSON backup file.")
    args = parser.parse_args()

    if args.restore:
        if args.restore == 'interactive':
            restore()
        else:
            restore(args.restore)
    else:
        main_menu()
