from datetime import datetime
from flask import (Blueprint,request,jsonify,)
from flask_login import (login_required,current_user,)
from database.database import db
from database.models import (User,Trek,Booking,)
from database.enums import UserRole
api = Blueprint("api",__name__,url_prefix="/api")
@api.route("/treks", methods=["GET"])
@login_required
def get_treks():
    treks = Trek.query.all()
    data = []
    for trek in treks:
        data.append({
            "id": trek.id,
            "name": trek.trek_name,
            "location": trek.location,
            "difficulty": trek.difficulty,
            "duration_days": trek.duration_days,
            "available_slots": trek.available_slots,
            "price": trek.price,
            "status": trek.status,
            "start_date": (
                trek.start_date.isoformat()
                if trek.start_date
                else None
            ),
            "end_date": (
                trek.end_date.isoformat()
                if trek.end_date
                else None
            ),
            "assigned_staff_id":
                trek.assigned_staff_id
        })
    return jsonify({
        "success": True,
        "count": len(data),
        "treks": data
    })
@api.route("/treks/<int:trek_id>", methods=["GET"])
@login_required
def get_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    return jsonify({
        "success": True,
        "trek": {
            "id": trek.id,
            "name": trek.trek_name,
            "location": trek.location,
            "difficulty": trek.difficulty,
            "duration_days": trek.duration_days,
            "available_slots":
                trek.available_slots,
            "price": trek.price,
            "status": trek.status,
            "start_date":
                trek.start_date.isoformat(),
            "end_date":
                trek.end_date.isoformat(),
            "assigned_staff_id":
                trek.assigned_staff_id
        }
    })
@api.route("/treks", methods=["POST"])
@login_required
def create_trek_api():
    if current_user.role != UserRole.ADMIN.value:
        return jsonify({
            "success": False,
            "message": "Administrator access required."
        }), 403
    data = request.get_json()
    if not data:
        return jsonify({
            "success": False,
            "message": "JSON request body required."
        }), 400
    required_fields = [
        "trek_name",
        "location",
        "difficulty",
        "duration_days",
        "available_slots",
        "price",
        "status",
        "start_date",
        "end_date",
        "assigned_staff_id"
    ]
    for field in required_fields:
        if field not in data:
            return jsonify({
                "success": False,
                "message":
                    f"Missing field: {field}"
            }), 400
    try:
        start_date = datetime.strptime(
            data["start_date"],
            "%Y-%m-%d"
        ).date()
        end_date = datetime.strptime(
            data["end_date"],
            "%Y-%m-%d"
        ).date()
    except ValueError:
        return jsonify({
            "success": False,
            "message":
                "Dates must use YYYY-MM-DD format."
        }), 400
    if end_date < start_date:
        return jsonify({
            "success": False,
            "message":
                "End date cannot be before start date."
        }), 400
    trek = Trek(
        trek_name=data["trek_name"],
        location=data["location"],
        difficulty=data["difficulty"],
        duration_days=int(
            data["duration_days"]
        ),
        available_slots=int(
            data["available_slots"]
        ),
        price=float(
            data["price"]
        ),
        status=data["status"],
        start_date=start_date,
        end_date=end_date,
        assigned_staff_id=int(
            data["assigned_staff_id"]
        )
    )
    db.session.add(trek)
    db.session.commit()
    return jsonify({
        "success": True,
        "message": "Trek created successfully.",
        "trek_id": trek.id
    }), 201
@api.route("/treks/<int:trek_id>", methods=["PUT"])
@login_required
def update_trek_api(trek_id):
    if current_user.role != UserRole.ADMIN.value:
        return jsonify({
            "success": False,
            "message": "Administrator access required."
        }), 403
    trek = Trek.query.get_or_404(trek_id)
    data = request.get_json()
    if not data:
        return jsonify({
            "success": False,
            "message": "JSON request body required."
        }), 400
    if "trek_name" in data:
        trek.trek_name = data["trek_name"]
    if "location" in data:
        trek.location = data["location"]
    if "difficulty" in data:
        trek.difficulty = data["difficulty"]
    if "duration_days" in data:
        trek.duration_days = int(
            data["duration_days"]
        )
    if "available_slots" in data:
        trek.available_slots = int(
            data["available_slots"]
        )
    if "price" in data:
        trek.price = float(
            data["price"]
        )
    if "status" in data:
        trek.status = data["status"]
    if "assigned_staff_id" in data:
        trek.assigned_staff_id = int(
            data["assigned_staff_id"]
        )
    db.session.commit()
    return jsonify({
        "success": True,
        "message": "Trek updated successfully."
    })
@api.route("/treks/<int:trek_id>", methods=["DELETE"])
@login_required
def delete_trek_api(trek_id):
    if current_user.role != UserRole.ADMIN.value:
        return jsonify({
            "success": False,
            "message": "Administrator access required."
        }), 403
    trek = Trek.query.get_or_404(trek_id)
    bookings = Booking.query.filter_by(
        trek_id=trek.id
    ).count()
    if bookings > 0:
        return jsonify({
            "success": False,
            "message":
                "Cannot delete a trek with bookings."
        }), 409
    db.session.delete(trek)
    db.session.commit()
    return jsonify({
        "success": True,
        "message": "Trek deleted successfully."
    })
@api.route("/users", methods=["GET"])
@login_required
def get_users():
    if current_user.role != UserRole.ADMIN.value:
        return jsonify({
            "success": False,
            "message": "Administrator access required."
        }), 403
    users = User.query.all()
    data = []
    for user in users:
        data.append({
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone_number": user.phone_number,
            "role": user.role,
            "is_active": user.is_active,
            "blacklisted":
                getattr(
                    user,
                    "blacklisted",
                    False
                ),
            "is_approved":
                getattr(
                    user,
                    "is_approved",
                    True
                )
        })
    return jsonify({
        "success": True,
        "count": len(data),
        "users": data
    })
@api.route("/users/<int:user_id>", methods=["PUT"])
@login_required
def update_user_api(user_id):
    if current_user.role != UserRole.ADMIN.value:
        return jsonify({
            "success": False,
            "message": "Administrator access required."
        }), 403
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    if "full_name" in data:
        user.full_name = data["full_name"]
    if "phone_number" in data:
        user.phone_number = data["phone_number"]
    if "role" in data:
        user.role = data["role"]
    if "is_active" in data:
        user.is_active = bool(
            data["is_active"]
        )
    if hasattr(user, "blacklisted"):
        if "blacklisted" in data:
            user.blacklisted = bool(
                data["blacklisted"]
            )
    if hasattr(user, "is_approved"):
        if "is_approved" in data:
            user.is_approved = bool(
                data["is_approved"]
            )
    db.session.commit()
    return jsonify({
        "success": True,
        "message": "User updated successfully."
    })
@api.route("/bookings", methods=["GET"])
@login_required
def get_bookings():
    if current_user.role == UserRole.ADMIN.value:
        bookings = Booking.query.all()
    else:
        bookings = Booking.query.filter_by(
            user_id=current_user.id
        ).all()
    data = []
    for booking in bookings:
        data.append({
            "id": booking.id,
            "user_id": booking.user_id,
            "trek_id": booking.trek_id,
            "booking_date":
                booking.booking_date.isoformat(),
            "booking_status":
                booking.booking_status,
            "payment_status":
                booking.payment_status,
            "number_of_people":
                booking.number_of_people,
            "total_amount":
                booking.total_amount
        })
    return jsonify({
        "success": True,
        "count": len(data),
        "bookings": data
    })
@api.route("/bookings", methods=["POST"])
@login_required
def create_booking_api():
    data = request.get_json()
    if not data or "trek_id" not in data:
        return jsonify({
            "success": False,
            "message": "trek_id is required."
        }), 400
    trek = Trek.query.get_or_404(
        int(data["trek_id"])
    )
    people = int(
        data.get("number_of_people", 1)
    )
    if people <= 0:
        return jsonify({
            "success": False,
            "message":
                "Number of people must be positive."
        }), 400
    if trek.available_slots < people:
        return jsonify({
            "success": False,
            "message":
                "Not enough available slots."
        }), 409
    existing = Booking.query.filter_by(
        user_id=current_user.id,
        trek_id=trek.id
    ).first()
    if existing:
        return jsonify({
            "success": False,
            "message":
                "You already booked this trek."
        }), 409
    booking = Booking(
        user_id=current_user.id,
        trek_id=trek.id,
        booking_status="Booked",
        payment_status="Pending",
        number_of_people=people,
        total_amount=(
            trek.price * people
        )
    )
    trek.available_slots -= people
    if trek.available_slots == 0:
        trek.status = "Closed"
    db.session.add(booking)
    db.session.commit()
    return jsonify({
        "success": True,
        "message":
            "Booking created successfully.",
        "booking_id":
            booking.id
    }), 201
@api.route("/bookings/<int:booking_id>", methods=["PUT"])
@login_required
def update_booking_api(booking_id):
    booking = Booking.query.get_or_404(
        booking_id
    )
    if (
        current_user.role !=
        UserRole.ADMIN.value
        and
        booking.user_id !=
        current_user.id
    ):
        return jsonify({
            "success": False,
            "message": "Unauthorized."
        }), 403
    data = request.get_json()
    if "payment_status" in data:
        booking.payment_status = (
            data["payment_status"]
        )
    if "booking_status" in data:
        booking.booking_status = (
            data["booking_status"]
        )
    db.session.commit()
    return jsonify({
        "success": True,
        "message":
            "Booking updated successfully."
    })
@api.route(
    "/bookings/<int:booking_id>",
    methods=["DELETE"]
)
@login_required
def delete_booking_api(booking_id):
    booking = Booking.query.get_or_404(
        booking_id
    )
    if booking.user_id != current_user.id:
        if current_user.role != UserRole.ADMIN.value:
            return jsonify({
                "success": False,
                "message": "Unauthorized."
            }), 403
    if booking.booking_status == "Cancelled":
        return jsonify({
            "success": False,
            "message": "Booking already cancelled."
        }), 409
    booking.booking_status = "Cancelled"
    booking.trek.available_slots += (
        booking.number_of_people
    )
    if booking.trek.available_slots > 0:
        booking.trek.status = "Open"
    db.session.commit()
    return jsonify({
        "success": True,
        "message":
            "Booking cancelled successfully."
    })
