"""
Gruha Alankara — Booking Routes
Handles furniture booking endpoints.
"""

import logging

from flask import Blueprint, request, jsonify

from services.booking_agent import BookingAgentService

logger = logging.getLogger(__name__)

booking_bp = Blueprint("booking", __name__)


@booking_bp.route("/book-furniture", methods=["POST"])
def book_furniture():
    """Book a furniture item (by product_id or product_name)."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Missing request body"}), 400

    service = BookingAgentService()
    user_id = data.get("user_id")

    if "product_id" in data:
        result = service.book(data["product_id"], user_id)
    elif "product_name" in data:
        result = service.book_by_name(data["product_name"], user_id)
    else:
        return jsonify({"success": False, "error": "Provide 'product_id' or 'product_name'"}), 400

    status_code = 200 if result["success"] else 404
    return jsonify(result), status_code


@booking_bp.route("/bookings", methods=["GET"])
def get_bookings():
    """Get all bookings or filter by user_id."""
    user_id = request.args.get("user_id", type=int)
    service = BookingAgentService()

    if user_id:
        bookings = service.get_user_bookings(user_id)
    else:
        bookings = service.get_all_bookings()

    return jsonify({
        "success": True,
        "bookings": bookings,
    })


@booking_bp.route("/cancel-booking", methods=["POST"])
def cancel_booking():
    """Cancel a booking by ID."""
    data = request.get_json(silent=True)
    if not data or "booking_id" not in data:
        return jsonify({"success": False, "error": "Missing 'booking_id'"}), 400

    service = BookingAgentService()
    result = service.cancel_booking(data["booking_id"])
    status_code = 200 if result["success"] else 404
    return jsonify(result), status_code
