"""
Gruha Alankara — Booking Agent Service
Handles automated furniture booking logic.
"""

import logging
from datetime import datetime, timezone

from database.db import db
from models.booking_model import Booking
from models.product_model import Product

logger = logging.getLogger(__name__)


class BookingAgentService:
    """Automates furniture booking workflow."""

    def book(self, product_id: int, user_id: int | None = None) -> dict:
        """
        Book a product by ID.

        Returns
        -------
        dict with booking confirmation or error.
        """
        product = Product.query.get(product_id)
        if not product:
            return {"success": False, "error": "Product not found"}

        booking = Booking(
            product_id=product.id,
            user_id=user_id,
            booking_status="confirmed",
            booking_date=datetime.now(timezone.utc),
        )
        db.session.add(booking)
        db.session.commit()

        logger.info("Booking created: id=%s product=%s", booking.id, product.product_name)

        return {
            "success": True,
            "booking_id": booking.id,
            "product_name": product.product_name,
            "price": product.price,
            "status": booking.booking_status,
            "booking_date": booking.booking_date.isoformat(),
            "message": f"Successfully booked '{product.product_name}' for ₹{product.price:,.0f}",
        }

    def book_by_name(self, product_name: str, user_id: int | None = None) -> dict:
        """
        Search for a product by name and book it.

        Parameters
        ----------
        product_name : str
            Partial or full product name.
        user_id : int | None
            Optional user id.
        """
        product = Product.query.filter(
            Product.product_name.ilike(f"%{product_name}%")
        ).first()

        if not product:
            return {"success": False, "error": f"No product matching '{product_name}' found in catalog"}

        return self.book(product.id, user_id)

    def get_user_bookings(self, user_id: int) -> list[dict]:
        """Return all bookings for a user."""
        bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.booking_date.desc()).all()
        return [b.to_dict() for b in bookings]

    def get_all_bookings(self) -> list[dict]:
        """Return all bookings."""
        bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
        return [b.to_dict() for b in bookings]

    def cancel_booking(self, booking_id: int) -> dict:
        """Cancel a booking."""
        booking = Booking.query.get(booking_id)
        if not booking:
            return {"success": False, "error": "Booking not found"}
        booking.booking_status = "cancelled"
        db.session.commit()
        return {"success": True, "message": f"Booking #{booking_id} cancelled"}
