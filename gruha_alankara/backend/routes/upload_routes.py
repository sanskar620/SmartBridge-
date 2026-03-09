"""
Gruha Alankara — Upload Routes
Handles room image upload and storage.
"""

import os
import logging

from flask import Blueprint, request, jsonify, current_app

from services.image_analysis import ImageAnalysisService

logger = logging.getLogger(__name__)

upload_bp = Blueprint("upload", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route("/upload-room", methods=["POST"])
def upload_room():
    """Upload a room image for analysis."""
    if "image" not in request.files:
        return jsonify({"success": False, "error": "No image file provided"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"success": False, "error": "Empty filename"}), 400

    if not _allowed_file(file.filename):
        return jsonify({"success": False, "error": "File type not allowed. Use JPG, PNG, or WEBP"}), 400

    storage_dir = current_app.config["ROOM_IMAGES_DIR"]
    service = ImageAnalysisService(storage_dir)
    filename = service.save_uploaded_image(file)

    return jsonify({
        "success": True,
        "filename": filename,
        "message": "Room image uploaded successfully",
    })


@upload_bp.route("/analyze-room", methods=["POST"])
def analyze_room():
    """Run AI analysis on a previously uploaded room image."""
    data = request.get_json(silent=True)
    if not data or "filename" not in data:
        return jsonify({"success": False, "error": "Missing 'filename' in request body"}), 400

    filename = data["filename"]
    storage_dir = current_app.config["ROOM_IMAGES_DIR"]
    service = ImageAnalysisService(storage_dir)

    try:
        analysis = service.analyze(filename)
    except FileNotFoundError:
        return jsonify({"success": False, "error": "Image file not found"}), 404
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400

    return jsonify({
        "success": True,
        "analysis": analysis,
    })
