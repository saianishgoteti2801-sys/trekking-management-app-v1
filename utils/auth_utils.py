from flask_login import current_user
from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)
from database.database import login_manager
from database.models import User
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
def hash_password(password):
    return generate_password_hash(password)
def verify_password(hashed_password, password):
    return check_password_hash(hashed_password,password)
def get_current_user():
    return current_user