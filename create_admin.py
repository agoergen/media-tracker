from app import create_app, db
from app.models import User
import sys

app = create_app()

def create_admin(username, password):
    with app.app_context():
        # Check if user already exists
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"User {username} already exists. Updating password.")
            user.set_password(password)
        else:
            print(f"Creating new admin user: {username}")
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
        
        db.session.commit()
        print("Success!")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python create_admin.py <username> <password>")
    else:
        create_admin(sys.argv[1], sys.argv[2])
