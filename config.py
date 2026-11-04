import os
from pathlib import Path
class Config:
    BASE_DIR = Path(__file__).resolve().parent
    DATABASE_NAME = "trekking-management-app-v1.db"
    DATABASE_PATH = BASE_DIR / "instance" / DATABASE_NAME
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY","Pune")
    RECORDS_PER_PAGE = 12
    UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024