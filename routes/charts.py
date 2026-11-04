from flask import (Blueprint,render_template,)
from flask_login import (login_required,current_user,)
from sqlalchemy import func
from database.database import db
from database.models import (User,Trek,Booking,)
from database.enums import UserRole
charts = Blueprint("charts",__name__,url_prefix="/charts")
@charts.route("/admin")
@login_required
def admin_charts():
    if current_user.role != UserRole.ADMIN.value:
        return "Unauthorized", 403
    total_treks = Trek.query.count()
    total_bookings = Booking.query.count()
    active_users = User.query.filter_by(is_active=True
    ).count()
    trek_labels = []
    trek_booking_counts = []
    treks = Trek.query.all()
    for trek in treks:
        trek_labels.append(trek.trek_name)
        count = Booking.query.filter_by(trek_id=trek.id
        ).count()
        trek_booking_counts.append(count)
    return render_template("admin/charts.html",total_treks=total_treks,total_bookings=total_bookings,active_users=active_users,trek_labels=trek_labels,trek_booking_counts=trek_booking_counts)
@charts.route("/staff")
@login_required
def staff_charts():
    if current_user.role != UserRole.STAFF.value:
        return "Unauthorized", 403
    treks = Trek.query.filter_by(
        assigned_staff_id=current_user.id
    ).all()
    trek_labels = []
    participant_counts = []
    for trek in treks:
        trek_labels.append(trek.trek_name)
        participant_count = db.session.query(
            func.coalesce(
                func.sum(Booking.number_of_people),0
            )
        ).filter(
            Booking.trek_id == trek.id,Booking.booking_status != "Cancelled"
        ).scalar()
        participant_counts.append(int(participant_count))
    return render_template("staff/charts.html",trek_labels=trek_labels,participant_counts=participant_counts)
@charts.route("/user")
@login_required
def user_charts():
    bookings = Booking.query.filter_by(user_id=current_user.id
    ).order_by(
        Booking.booking_date.asc()
    ).all()
    labels = []
    booking_values = []
    for booking in bookings:
        labels.append(booking.booking_date.strftime("%d-%m-%Y"))
        booking_values.append(booking.number_of_people)
    return render_template("user/charts.html",labels=labels,booking_values=booking_values)