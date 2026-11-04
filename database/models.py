from datetime import datetime
from flask_login import UserMixin
from database.database import db
from database.enums import (UserRole,TrekDifficulty,TrekStatus,BookingStatus,PaymentStatus,)
class User(UserMixin, db.Model):
    __tablename__ = "users_details"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120),nullable=False)
    email = db.Column(db.String(120),unique=True,nullable=False)
    password_hash = db.Column(db.String(255),nullable=False)
    role = db.Column(db.String(50),nullable=False,default=UserRole.TREKKER.value)
    is_active = db.Column(db.Boolean,default=True)
    blacklisted = db.Column(db.Boolean,default=False,nullable=False)
    is_approved = db.Column(db.Boolean,default=False)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)
    updated_at = db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
    phone_number = db.Column(db.String(15),unique=True,nullable=True)
    def __repr__(self):
        return (
            f"<User {self.id}: "
            f"{self.full_name} "
            f"({self.role})>"
        )
    def __str__(self):
        return self.full_name
    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN.value
    @property
    def is_staff(self):
        return self.role == UserRole.STAFF.value
    @property
    def is_trekker(self):
        return self.role == UserRole.TREKKER.value
class StaffProfile(db.Model):
    __tablename__ = "staff_profiles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey("users_details.id"),unique=True,nullable=False)
    experience = db.Column(db.Integer,default=0)
    specialization = db.Column(db.String(100),nullable=False)
    address = db.Column(db.String(250))
    emergency_contact = db.Column(db.String(15))
    user = db.relationship("User",
        backref=db.backref(
            "staff_profile",
            uselist=False
        )
    )
    def __repr__(self):
        return (
            f"<StaffProfile {self.id}: "
            f"{self.specialization}>"
        )    
class Trek(db.Model):    
    __tablename__ = "treks_events"
    id = db.Column(db.Integer,primary_key=True)
    trek_name = db.Column(db.String(150),nullable=False)
    location = db.Column(db.String(150),nullable=False)
    difficulty = db.Column(db.String(25),nullable=False)
    duration_days = db.Column(db.Integer,nullable=False)
    available_slots = db.Column(db.Integer,nullable=False)
    price = db.Column(db.Float,nullable=False)
    status = db.Column(db.String(25),nullable=False)
    start_date = db.Column(db.Date,nullable=False)
    end_date = db.Column(db.Date,nullable=False)
    assigned_staff_id = db.Column(db.Integer,db.ForeignKey("users_details.id"),nullable=False)
    brochure_filename = db.Column(db.String(255),nullable=True)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)
    assigned_staff = db.relationship("User",backref="assigned_treks")
    def __repr__(self):
        return (
            f"<Trek {self.id}: "
            f"{self.trek_name}>"
        )    
class Booking(db.Model):
    __tablename__ = "bookings_details"
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey("users_details.id"),nullable=False)
    trek_id = db.Column(db.Integer,db.ForeignKey("treks_events.id"),nullable=False)
    booking_date = db.Column(db.DateTime,default=datetime.utcnow)
    booking_status = db.Column(db.String(30),nullable=False)
    payment_status = db.Column(db.String(30),nullable=False)
    number_of_people = db.Column(db.Integer,default=1)
    discount = db.Column(db.Float,default=0)
    coupon_code = db.Column(db.String(30))
    payment_method = db.Column(db.String(30))
    total_amount = db.Column(db.Float,nullable=False)
    user = db.relationship("User",backref="bookings_details")
    trek = db.relationship("Trek",backref="bookings_details")
    def __repr__(self):
        return (
            f"<Booking {self.id}: "
            f"User {self.user_id} "
            f"-> Trek {self.trek_id}>"
        )