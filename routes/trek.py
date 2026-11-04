from flask import (Blueprint,render_template,request,url_for,redirect,flash,send_from_directory,current_app,)
from flask_login import (current_user,login_required,)
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash
from database.database import db
from database.models import User
from sqlalchemy import or_
from database.models import Trek
import os
trek = Blueprint("trek",__name__)
@trek.route("/dashboard")
@login_required
def dashboard():
    search = request.args.get("search","")
    query = Trek.query.filter_by(status="Open")
    if search:
        query = query.filter(
            or_(
                Trek.trek_name.ilike(f"%{search}%"),
                Trek.location.ilike(f"%{search}%"),
                Trek.difficulty.ilike(f"%{search}%")
            )
        )
    treks = query.all()
    return render_template("user/dashboard.html",treks=treks,search=search,
        background_image=url_for(
            "static",
            filename="img/user.jpg"
        )
    )
@trek.route("/brochure/<int:trek_id>")
@login_required
def download_brochure(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if not trek.brochure_filename:
        flash("No brochure has been uploaded for this trek.","warning")
        return redirect(url_for("trek.dashboard"))
    return send_from_directory(
        os.path.join(current_app.static_folder, "brochures"),
        trek.brochure_filename,
        as_attachment=True
    )
@trek.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone_number = request.form.get("phone_number", "").strip()
        if not full_name:
            flash("Full name is required.", "danger")
            return redirect(url_for("trek.profile"))
        if not email:
            flash("Email address is required.", "danger")
            return redirect(url_for("trek.profile"))
        existing_user = User.query.filter(
            User.email == email,
            User.id != current_user.id
        ).first()
        if existing_user:
            flash("That email address is already registered.","danger")
            return redirect(url_for("trek.profile"))
        current_user.full_name = full_name
        current_user.email = email
        current_user.phone_number = phone_number
        db.session.commit()
        flash("Profile updated successfully.","success")
        return redirect(url_for("trek.profile"))
    return render_template("user/profile.html",user=current_user,
        background_image=url_for(
            "static",
            filename="img/user.jpg"
        )
    )
@trek.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        current_password = request.form.get("current_password","")
        new_password = request.form.get("new_password","")
        confirm_password = request.form.get("confirm_password","")
        if not current_password:
            flash("Current password is required.","danger")
            return redirect(url_for("trek.settings"))
        if len(new_password) < 6:
            flash("New password must contain at least 6 characters.","danger")
            return redirect(url_for("trek.settings"))
        if new_password != confirm_password:
            flash("New password and confirmation do not match.","danger")
            return redirect(url_for("trek.settings"))
        if not check_password_hash(current_user.password_hash,current_password
        ):
            flash("Current password is incorrect.","danger")
            return redirect(url_for("trek.settings"))
        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash("Password changed successfully.","success")
        return redirect(url_for("trek.settings"))
    return render_template("user/settings.html",user=current_user,
        background_image=url_for(
            "static",
            filename="img/user.jpg"
        )
    )