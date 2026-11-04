from enum import Enum
class UserRole(Enum):
    ADMIN = "Admin"
    STAFF = "Staff"
    TREKKER = "Trekker"
class TrekDifficulty(Enum):
    EASY = "Easy"
    MODERATE = "Moderate"
    HARD = "Hard"
class TrekStatus(Enum):
    OPEN = "Open"
    CLOSED = "Closed"
    ONGOING = "Ongoing"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
class BookingStatus(Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"
class PaymentStatus(Enum):
    PENDING = "Pending"
    PAID = "Paid"
    REFUNDED = "Refunded"