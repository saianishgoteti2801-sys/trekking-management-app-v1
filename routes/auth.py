from flask import (Blueprint,render_template,request,redirect,url_for,flash,)
from flask_login import (login_user,logout_user,login_required,)
from database.database import db
from database.models import User
from database.enums import UserRole
from utils.auth_utils import (hash_password,verify_password,)
auth = Blueprint("auth",__name__,)
@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone_number = request.form.get("phone_number", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", UserRole.TREKKER.value)
        if not full_name or not email or not password:
            flash("Please fill in all required fields.","danger")
            return redirect(
                url_for("trek.dashboard")
            )
        if role == UserRole.ADMIN.value:
            flash("Administrator account cannot be created here.","danger")
            return redirect(url_for("auth.register"))
        existing_user = User.query.filter_by(
            email=email
        ).first()
        if existing_user:
            flash("Email is already registered.","warning")
            return redirect(url_for("auth.register"))
        if phone_number:
            existing_phone = User.query.filter_by(
                    phone_number=phone_number
            ).first()
            if existing_phone:
                flash("Phone number already exists.","warning")
                return redirect(url_for("auth.register"))
        new_user = User(full_name=full_name,email=email,phone_number=phone_number,password_hash=hash_password(password),role=role,is_active=True)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. Please login.","success")
        return redirect(
            url_for("auth.login")
        )
    return render_template("register.html",
        background_image=url_for(
            "static",filename="img/register.jpg"
        )
    )
@auth.route("/select-role")
def select_role():
    return render_template("role_selection.html")
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        if not email or not password:
            flash("Email and Password are required.","danger")
            return redirect(
                url_for("auth.login")
            )
        user = User.query.filter_by(email=email
        ).first()
        if not user:
            flash("No account found with this email.","warning")
            return redirect(
                url_for("auth.login")
            )
        if not user.is_active:
            flash("Your account has been deactivated.","danger")
            return redirect(
                url_for("auth.login")
            )
        if not verify_password(user.password_hash,password
        ):
            flash("Incorrect password.","danger")
            return redirect(
                url_for("auth.login")
            )
        remember = request.form.get("remember") == "on"
        login_user(user,remember=remember)
        flash(f"Welcome {user.full_name}!","success")
        if user.is_admin:
            return redirect(
                url_for("admin.dashboard")
            )
        if user.is_staff:
            return redirect(
                url_for("staff.dashboard")
            )
        return redirect(
            url_for("trek.dashboard")
        )
    return render_template("login.html",
        background_image=url_for("static",filename="img/login.jpg"
        )
    )
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.","info")
    return redirect(
        url_for("auth.login")
    )