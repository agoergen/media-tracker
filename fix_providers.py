from app import create_app, db
from app.models import Movie

app = create_app()

def fix_disney():
    with app.app_context():
        # Fix Disney+ to Disney Plus
        disney_count = Movie.query.filter_by(provider='Disney+').update({Movie.provider: 'Disney Plus'})
        
        # Fix HBO Max/Max consistency if needed
        # (Optional: you could also fix others like 'Apple TV+')
        
        db.session.commit()
        print(f"Fixed {disney_count} Disney+ records.")

if __name__ == '__main__':
    fix_disney()
