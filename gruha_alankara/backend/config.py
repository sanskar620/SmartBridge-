"""
Gruha Alankara — Configuration Module
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "gruha-alankara-secret-key-change-in-production")

    # Database
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "database", "gruha_alankara.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload settings
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

    # Storage paths
    STORAGE_DIR = os.path.join(BASE_DIR, "storage")
    ROOM_IMAGES_DIR = os.path.join(STORAGE_DIR, "room_images")
    GENERATED_DESIGNS_DIR = os.path.join(STORAGE_DIR, "generated_designs")
    PRODUCT_ASSETS_DIR = os.path.join(STORAGE_DIR, "product_assets")

    # Server
    HOST = "0.0.0.0"
    PORT = 5000
    DEBUG = True
