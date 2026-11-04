from flask import Flask
from config import Config
from database.database import db
from database.models import (User,StaffProfile,Trek,Booking,)
def create_database():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    with app.app_context():
        Config.DATABASE_PATH.parent.mkdir(parents=True,exist_ok=True)
        db.create_all()
        print("=" * 60)
        print(" Trek Management Database Created Successfully ")
        print("=" * 60)
        print("\nTables Created:")
        for table in db.metadata.tables.keys():
            print(f"✓ {table}")
if __name__ == "__main__":
    create_database()