from datetime import datetime
from flask import (Blueprint,redirect,url_for,flash,render_template,)
from flask_login import (login_required,current_user,)
from database.database import db
from database.models import (Trek,Booking,)
booking = Blueprint("booking",__name__)
@booking.route("/book/<int:trek_id>")
@login_required
def book_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if trek.status != "Open":
        flash("Booking is closed.","danger")
        return redirect(
            url_for("trek.dashboard")
        )
    if trek.available_slots <= 0:
        flash("No slots available.","danger")
        return redirect(
            url_for("trek.dashboard")
        )
    duplicate = Booking.query.filter_by(user_id=current_user.id,trek_id=trek.id
    ).first()
    if duplicate:
        flash("You have already booked this trek.","warning")
        return redirect(
            url_for("trek.dashboard")
        )
    booking = Booking(user_id=current_user.id,trek_id=trek.id,booking_status="Booked",payment_status="Paid",number_of_people=1,total_amount=trek.price)
    db.session.add(booking)
    trek.available_slots -= 1
    if trek.available_slots == 0:
        trek.status = "Closed"
    db.session.commit()
    flash("Booking successful.","success")
    return redirect(
        url_for("booking.history")
    )
@booking.route("/history")
@login_required
def history():
    bookings = Booking.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Booking.booking_date.desc()
    ).all()
    return render_template("user/history.html",bookings=bookings)
@booking.route("/cancel/<int:booking_id>")
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        flash("Unauthorized access.","danger")
        return redirect(
            url_for("booking.history")
        )
    if booking.booking_status != "Booked":
        flash("Only active bookings can be cancelled.","warning")
        return redirect(
            url_for("booking.history")
        )
    booking.booking_status = "Cancelled"
    booking.trek.available_slots += 1
    booking.trek.status = "Open"
    db.session.commit()
    flash("Booking cancelled successfully.","success")
    return redirect(
        url_for("booking.history")
    )
