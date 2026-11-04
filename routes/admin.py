from re import search
from flask import (Blueprint,render_template,request,redirect,url_for,flash,send_from_directory,current_app,)
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from database.database import db
from database.enums import UserRole
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from utils.decorators import admin_required
from database.models import (User,Trek,Booking,)
UPLOAD_FOLDER = "brochures"
ALLOWED_BROCHURE_EXTENSIONS = {"pdf"}

def save_brochure(file):
    if not file or not file.filename:
        return None
    original_name = secure_filename(file.filename)
    if not original_name or "." not in original_name:
        return None
    extension = original_name.rsplit(".", 1)[1].lower()
    if extension not in ALLOWED_BROCHURE_EXTENSIONS:
        return None
    filename = f"{uuid.uuid4().hex}_{original_name}"
    upload_path = os.path.join(current_app.static_folder,UPLOAD_FOLDER)
    os.makedirs(upload_path, exist_ok=True)
    file.save(os.path.join(upload_path, filename))
    return filename

admin = Blueprint("admin",__name__,)
@admin.route("/dashboard")
@admin_required
def dashboard():
    total_users = User.query.count()
    total_staff = User.query.filter_by(
        role=UserRole.STAFF.value
    ).count()
    total_trekkers = User.query.filter_by(
        role=UserRole.TREKKER.value
    ).count()
    total_admins = User.query.filter_by(
        role=UserRole.ADMIN.value
    ).count()
    total_treks = Trek.query.count()
    open_treks = Trek.query.filter_by(
        status="Open"
    ).count()
    closed_treks = Trek.query.filter_by(
        status="Closed"
    ).count()
    total_bookings = Booking.query.count()
    return render_template("admin/dashboard.html",total_users=total_users,total_staff=total_staff,total_trekkers=total_trekkers,total_admins=total_admins,total_treks=total_treks,open_treks=open_treks,closed_treks=closed_treks,total_bookings=total_bookings,
                           background_image=url_for("static",filename="img/admin.jpg"))
@admin.route("/treks")
@admin_required
def manage_treks():
    search = request.args.get("search","")
    query = Trek.query
    if search:
        from sqlalchemy import or_
        query = query.filter(
            or_(
                Trek.trek_name.ilike(f"%{search}%"),
                Trek.location.ilike(f"%{search}%"),
                Trek.difficulty.ilike(f"%{search}%")
            )
        )
    treks = query.order_by(
        Trek.start_date.asc()
    ).all()
    return render_template(
        "admin/manage_treks.html",
        treks=treks,
        search=search
    )
@admin.route("/treks/create", methods=["GET", "POST"])
@admin_required
def create_trek():
    staff_members = User.query.filter_by(
        role=UserRole.STAFF.value
    ).all()
    if request.method == "POST":
        required_fields = ["trek_name","location","difficulty","duration_days","available_slots","price","status","start_date","end_date","assigned_staff",]
        for field in required_fields:
            if not request.form.get(field):
                flash(
                    f"{field.replace('_', ' ').title()} is required.",
                    "danger"
                )
                return redirect(
                    url_for("admin.create_trek")
                )
        start_date = datetime.strptime(
            request.form.get("start_date"),
            "%Y-%m-%d"
        ).date()
        end_date = datetime.strptime(
            request.form.get("end_date"),
            "%Y-%m-%d"
        ).date()
        if end_date < start_date:
            flash(
                "End date cannot be before Start date.",
                "danger"
            )
            return redirect(
                url_for("admin.create_trek")
            )
        brochure_file = request.files.get("brochure")
        brochure_filename = None

        if brochure_file and brochure_file.filename:
            brochure_filename = save_brochure(brochure_file)
            if brochure_filename is None:
                flash("Only PDF brochure files are allowed.","danger")
                return redirect(url_for("admin.create_trek"))

        trek = Trek(trek_name=request.form.get("trek_name"),location=request.form.get("location"),difficulty=request.form.get("difficulty"),
            duration_days=int(
                request.form.get("duration_days")
            ),
            available_slots=int(
                request.form.get("available_slots")
            ),
            price=float(
                request.form.get("price")
            ),
            status = request.form.get("status"),
            start_date=start_date,
            end_date=end_date,
            assigned_staff_id=int(
                request.form.get("assigned_staff")
            ),
            brochure_filename=brochure_filename
        )
        db.session.add(trek)
        db.session.commit()
        flash("New trek added successfully.","success")
        return redirect(
            url_for("admin.manage_treks")
        )
    return render_template("admin/create_trek.html",staff_members=staff_members)
@admin.route("/treks/edit/<int:trek_id>", methods=["GET", "POST"])
@admin_required
def edit_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    staff_members = User.query.filter_by(
        role=UserRole.STAFF.value
    ).all()
    if request.method == "POST":
        trek.trek_name = request.form.get("trek_name")
        trek.location = request.form.get("location")
        trek.difficulty = request.form.get("difficulty")
        trek.duration_days = int(
            request.form.get("duration_days")
        )
        trek.available_slots = int(
            request.form.get("available_slots")
        )
        trek.price = float(
            request.form.get("price")
        )
        trek.status = request.form.get("status")
        trek.start_date = datetime.strptime(
            request.form.get("start_date"),
            "%Y-%m-%d"
        ).date()
        trek.end_date = datetime.strptime(
            request.form.get("end_date"),
            "%Y-%m-%d"
        ).date()
        trek.assigned_staff_id = int(
            request.form.get("assigned_staff")
        )

        brochure_file = request.files.get("brochure")
        if brochure_file and brochure_file.filename:
            brochure_filename = save_brochure(brochure_file)
            if brochure_filename is None:
                flash("Only PDF brochure files are allowed.","danger")
                return redirect(
                    url_for("admin.edit_trek", trek_id=trek.id)
                )
            trek.brochure_filename = brochure_filename

        db.session.commit()
        flash("Trek updated successfully.","success")
        return redirect(url_for("admin.manage_treks"))
    return render_template("admin/edit_trek.html",trek=trek,staff_members=staff_members)
@admin.route("/treks/brochure/<int:trek_id>")
@admin_required
def download_brochure(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if not trek.brochure_filename:
        flash("No brochure has been uploaded for this trek.","warning")
        return redirect(url_for("admin.manage_treks"))
    return send_from_directory(
        os.path.join(current_app.static_folder, UPLOAD_FOLDER),
        trek.brochure_filename,
        as_attachment=True
    )

@admin.route("/treks/delete/<int:trek_id>")
@admin_required
def delete_trek(trek_id):
    trek = Trek.query.get_or_404(
        trek_id
    )
    if trek.bookings_details:
        flash("Cannot delete a trek with existing bookings.","danger")
        return redirect(
            url_for("admin.manage_treks")
        )
    db.session.delete(
        trek
    )
    db.session.commit()
    flash("Trek deleted successfully.","success")
    return redirect(
        url_for("admin.manage_treks")
    )
@admin.route("/users")
@admin_required
def manage_users():
    search = request.args.get("search","")
    query = User.query
    if search:
        query = query.filter(
            or_(
                User.full_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.phone_number.ilike(f"%{search}%")
            )
        )
    users = query.order_by(
        User.full_name.asc()
    ).all()
    return render_template("admin/manage_users.html",users=users,search=search)
@admin.route("/users/blacklist/<int:user_id>")
@login_required
@admin_required
def blacklist_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == UserRole.ADMIN.value:
        flash("Administrators cannot be blacklisted.","warning")
        return redirect(
            url_for("admin.manage_users")
        )
    user.blacklisted = True
    db.session.commit()
    flash(f"{user.full_name} has been blacklisted.","success")
    return redirect(
        url_for("admin.manage_users")
    )
@admin.route("/users/toggle/<int:user_id>")
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == UserRole.ADMIN.value:
        flash("Administrator account cannot be modified.","warning")
        return redirect(
            url_for("admin.manage_users")
        )
    user.is_active = not user.is_active
    db.session.commit()
    flash("User status updated successfully.","success")
    return redirect(
        url_for("admin.manage_users")
    ) 
@admin.route("/staff")
@admin_required
def manage_staff():
    search = request.args.get("search", "")
    query = User.query.filter_by(
        role=UserRole.STAFF.value
    )
    if search:
        query = query.filter(
            User.full_name.ilike(f"%{search}%")
        )
    staff_members = query.order_by(
        User.full_name.asc()
    ).all()
    return render_template("admin/manage_staff.html",staff_members=staff_members,search=search)
@admin.route("/staff/approve/<int:user_id>")
@admin_required
def approve_staff(user_id):
    staff = User.query.get_or_404(
        user_id
    )
    if staff.role != UserRole.STAFF.value:
        flash("Selected user is not a staff member.","danger"
        )
        return redirect(
            url_for("admin.manage_staff")
        )
    staff.is_active = True
    db.session.commit()
    flash("Staff approved successfully.","success")
    return redirect(url_for("admin.manage_staff"))
@admin.route("/staff/deactivate/<int:user_id>")
@admin_required
def deactivate_staff(user_id):
    staff = User.query.get_or_404(user_id)
    if staff.role != UserRole.STAFF.value:
        flash("Selected user is not a staff member.","danger")
        return redirect(
            url_for("admin.manage_staff")
        )
    staff.is_active = False
    db.session.commit()
    flash("Staff deactivated successfully.","success")
    return redirect(
        url_for("admin.manage_staff")
    )
@admin.route("/profile", methods=["GET", "POST"])
@admin_required
def profile():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone_number = request.form.get("phone_number", "").strip()
        if not full_name:
            flash("Full name is required.", "danger")
            return redirect(url_for("admin.profile"))
        if not email:
            flash("Email address is required.", "danger")
            return redirect(url_for("admin.profile"))
        existing_user = User.query.filter(
            User.email == email,User.id != current_user.id
        ).first()
        if existing_user:
            flash("That email address is already registered.", "danger")
            return redirect(url_for("admin.profile"))
        current_user.full_name = full_name
        current_user.email = email
        current_user.phone_number = phone_number
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("admin.profile"))
    return render_template("admin/profile.html",user=current_user)
@admin.route("/settings", methods=["GET", "POST"])
@admin_required
def settings():
    if request.method == "POST":
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")
        if not current_password:
            flash("Current password is required.", "danger")
            return redirect(url_for("admin.settings"))
        if not new_password:
            flash("New password is required.", "danger")
            return redirect(url_for("admin.settings"))
        if len(new_password) < 6:
            flash("New password must contain at least 6 characters.", "danger")
            return redirect(url_for("admin.settings"))
        if new_password != confirm_password:
            flash("New password and confirmation do not match.", "danger")
            return redirect(url_for("admin.settings"))
        if not check_password_hash(
            current_user.password_hash,
            current_password
        ):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for("admin.settings"))
        current_user.password_hash = generate_password_hash(
            new_password
        )
        db.session.commit()
        flash("Password changed successfully.", "success")
        return redirect(url_for("admin.settings"))
    return render_template("admin/settings.html",user=current_user)
@admin.route("/bookings")
@admin_required
def manage_bookings():
    search = request.args.get("search","")
    Booking.query.options(
        db.joinedload(Booking.user),
        db.joinedload(Booking.trek)
    )
    query = Booking.query.options(
        joinedload(Booking.user),
        joinedload(Booking.trek)
    )
    if search:
        query = query.join(User).join(Trek).filter(
            or_(
                User.full_name.ilike(f"%{search}%"),
                Trek.trek_name.ilike(f"%{search}%")
            )
        )
    bookings = query.order_by(
        Booking.booking_date.desc()
    ).all()
    return render_template("admin/manage_bookings.html",bookings=bookings,search=search)