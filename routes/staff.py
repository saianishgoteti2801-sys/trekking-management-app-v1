from flask import (Blueprint,render_template,request,redirect,url_for,flash,send_from_directory,current_app,)
from flask_login import current_user
import os
from werkzeug.security import generate_password_hash, check_password_hash
from database.database import db
from database.models import (Trek,Booking,StaffProfile,)
from database.enums import TrekStatus
from utils.decorators import staff_required
staff = Blueprint("staff",__name__)
@staff.route("/dashboard")
@staff_required
def dashboard():
    assigned_treks = Trek.query.filter_by(
        assigned_staff_id=current_user.id
    ).all()
    total_treks = len(assigned_treks)
    participant_count = 0
    for trek in assigned_treks:
        participant_count += len(trek.bookings_details)
    return render_template("staff/dashboard.html",assigned_treks=assigned_treks,total_treks=total_treks,participant_count=participant_count,background_image=url_for("static",filename="img/staff.jpg"))
@staff.route("/trek/<int:trek_id>", methods=["GET", "POST"])
@staff_required
def view_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != current_user.id:
        flash("You are not assigned to this trek.","danger")
        return redirect(
            url_for("staff.dashboard")
        )
    participants = Booking.query.filter_by(
        trek_id=trek.id
    ).all()
    for booking in participants:
        if (
            trek.status == "Completed" and booking.booking_status == "Booked"
            ):
            booking.booking_status = "Completed"
    db.session.commit()
    participant_count = len(participants)
    if request.method == "POST":
        trek.available_slots = int(request.form.get("available_slots"))
        if trek.available_slots < 0:
            flash("Available slots cannot be negative.","danger")
            return redirect(
                url_for("staff.view_trek",trek_id=trek.id)
            )
        trek.status = request.form.get("status")
        db.session.commit()
        flash("Trek updated successfully.","success")
        return redirect(url_for("staff.view_trek", trek_id=trek.id))
    return render_template("staff/view_trek.html",trek=trek,participants=participants,participant_count=participant_count)
@staff.route("/brochure/<int:trek_id>")
@staff_required
def download_brochure(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != current_user.id:
        flash("You are not assigned to this trek.","danger")
        return redirect(url_for("staff.dashboard"))
    if not trek.brochure_filename:
        flash("No brochure has been uploaded for this trek.","warning")
        return redirect(
            url_for("staff.view_trek", trek_id=trek.id)
        )
    return send_from_directory(
        os.path.join(current_app.static_folder, "brochures"),trek.brochure_filename,as_attachment=True
    )
@staff.route("/profile", methods=["GET", "POST"])
@staff_required
def profile():
    profile = StaffProfile.query.filter_by(
        user_id=current_user.id
    ).first()
    if profile is None:
        profile = StaffProfile(user_id=current_user.id,specialization="",experience=0)
        db.session.add(profile)
        db.session.commit()
    if request.method == "POST":
        profile.specialization = request.form.get("specialization")
        profile.experience = int(request.form.get("experience"))
        profile.address = request.form.get("address")
        profile.emergency_contact = request.form.get("emergency_contact")
        db.session.commit()
        flash("Profile updated successfully.","success")
        return redirect(
            url_for("staff.profile")
        )
    return render_template("staff/profile.html",profile=profile,
        background_image=url_for("static",
            filename="img/staff.jpg"
        )
    )

@staff.route("/settings", methods=["GET", "POST"])
@staff_required
def settings():
    if request.method == "POST":
        current_password = request.form.get("current_password","")
        new_password = request.form.get("new_password","")
        confirm_password = request.form.get("confirm_password","")
        if not current_password:
            flash("Current password is required.","danger")
            return redirect(url_for("staff.settings"))
        if len(new_password) < 6:
            flash("New password must contain at least 6 characters.","danger")
            return redirect(url_for("staff.settings"))
        if new_password != confirm_password:
            flash("New password and confirmation do not match.","danger")
            return redirect(url_for("staff.settings"))
        if not check_password_hash(
            current_user.password_hash,
            current_password
        ):
            flash("Current password is incorrect.","danger")
            return redirect(url_for("staff.settings"))
        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash("Password changed successfully.","success")
        return redirect(url_for("staff.settings"))
    return render_template("staff/settings.html",user=current_user,
        background_image=url_for(
            "static",
            filename="img/staff.jpg"
        )
    )
