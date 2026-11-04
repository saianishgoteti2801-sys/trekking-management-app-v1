from flask import Flask, redirect, render_template, url_for 
from routes.staff import staff
from config import Config
from database.database import (db,migrate,login_manager)
from routes.auth import auth
from routes.admin import admin
from routes.trek import trek
from routes.booking import booking
from routes.api import api
from routes.charts import charts
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    app.register_blueprint(auth)
    app.register_blueprint(admin,url_prefix="/admin")
    app.register_blueprint(staff,url_prefix="/staff")
    app.register_blueprint(trek,url_prefix="/user")
    app.register_blueprint(booking,url_prefix="/booking")
    app.register_blueprint(api)
    app.register_blueprint(charts)
    @app.route("/")
    def home():
        return redirect(
            url_for("auth.select_role")
        )
    return app
app = create_app()
if __name__ == "__main__":
    app.run(debug=True,host="127.0.0.1",port=5000)
