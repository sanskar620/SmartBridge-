"""
Gruha Alankara — Booking Model
"""

from datetime import datetime, timezone
from database.db import db


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    booking_status = db.Column(db.String(50), default="pending")
    booking_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    product = db.relationship("Product", backref="bookings")

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "user_id": self.user_id,
            "booking_status": self.booking_status,
            "booking_date": self.booking_date.isoformat() if self.booking_date else None,
            "product_name": self.product.product_name if self.product else None,
        }
