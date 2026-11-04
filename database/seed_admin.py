from flask import Flask
from werkzeug.security import generate_password_hash
from config import Config
from database.database import db
from database.models import User
from database.enums import UserRole
def seed_admin():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    with app.app_context():
        admin = User.query.filter_by(
            email="admin@ds.study.iitm.ac.in"
        ).first()
        if admin:
            print("=" * 60)
            print("Administrator already exists.")
            print("=" * 60)
            return
        admin = User(
            full_name="System Administrator",
            email="admin@ds.study.iitm.ac.in",
            phone_number="9999999999",
            password_hash=generate_password_hash(
                "Admin@123"
            ),
            role=UserRole.ADMIN.value,
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("=" * 60)
        print("Administrator account created successfully.")
        print("=" * 60)
        print(f"Email    : {admin.email}")
        print("Password : Admin@123")
if __name__ == "__main__":
    seed_admin()