"""
Gruha Alankara — Main Flask Application
AI Interior Design Platform with AR and Agentic AI

Run with:
    cd gruha_alankara/backend
    python app.py

Server starts at: http://localhost:5000
"""

import os
import sys
import logging

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from config import Config
from database.db import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    """Application factory."""
    app = Flask(__name__, static_folder=None)
    app.config.from_object(config_class)

    # Enable CORS for frontend communication
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Ensure storage directories exist
    for dir_path in (
        app.config["ROOM_IMAGES_DIR"],
        app.config["GENERATED_DESIGNS_DIR"],
        app.config["PRODUCT_ASSETS_DIR"],
    ):
        os.makedirs(dir_path, exist_ok=True)

    # Ensure database directory exists
    db_dir = os.path.join(os.path.dirname(__file__), "database")
    os.makedirs(db_dir, exist_ok=True)

    # Initialize database
    init_db(app)

    # Register blueprints
    from routes.upload_routes import upload_bp
    from routes.design_routes import design_bp
    from routes.booking_routes import booking_bp
    from routes.voice_routes import voice_bp

    app.register_blueprint(upload_bp)
    app.register_blueprint(design_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(voice_bp)

    # ---- Serve frontend static files ----
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    @app.route("/")
    def serve_index():
        return send_from_directory(frontend_dir, "index.html")

    @app.route("/<path:filename>")
    def serve_static(filename):
        # Only serve known frontend files
        if filename in ("style.css", "script.js"):
            return send_from_directory(frontend_dir, filename)
        return jsonify({"error": "Not found"}), 404

    # ---- Health check ----
    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "service": "Gruha Alankara Backend"})

    # ---- Error handlers ----
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"success": False, "error": "Bad request"}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Endpoint not found"}), 404

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({"success": False, "error": "File too large. Maximum size is 10 MB."}), 413

    @app.errorhandler(500)
    def internal_error(e):
        logger.exception("Internal server error")
        return jsonify({"success": False, "error": "Internal server error"}), 500

    logger.info("Gruha Alankara backend initialized successfully")
    return app


if __name__ == "__main__":
    app = create_app()
    print("\n" + "=" * 60)
    print("  Gruha Alankara — AI Interior Design Platform")
    print("  Server running at: http://localhost:5000")
    print("=" * 60 + "\n")
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
    )
