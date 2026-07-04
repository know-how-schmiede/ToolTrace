from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'tooltrace.sqlite3'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    STORAGE_PATH = Path(os.environ.get("STORAGE_PATH", BASE_DIR / "storage"))
    MAX_UPLOAD_SIZE_MB = int(os.environ.get("MAX_UPLOAD_SIZE_MB", "20"))
    MAX_CONTENT_LENGTH = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    ALLOWED_IMAGE_TYPES = {
        item.strip().lower()
        for item in os.environ.get("ALLOWED_IMAGE_TYPES", "jpg,jpeg,png").split(",")
    }
    MIN_IMAGE_WIDTH = int(os.environ.get("MIN_IMAGE_WIDTH", "1200"))
    MIN_IMAGE_HEIGHT = int(os.environ.get("MIN_IMAGE_HEIGHT", "1200"))

    PROCESSING_PIXELS_PER_MM = float(os.environ.get("PROCESSING_PIXELS_PER_MM", "10"))
    DEFAULT_CONTOUR_OFFSET_MM = float(os.environ.get("DEFAULT_CONTOUR_OFFSET_MM", "1.5"))
    DEFAULT_CONTOUR_SIMPLIFICATION_MM = float(
        os.environ.get("DEFAULT_CONTOUR_SIMPLIFICATION_MM", "0.2")
    )
    DEFAULT_LAYOUT_TYPE = os.environ.get("DEFAULT_LAYOUT_TYPE", "gridfinity")
    GRIDFINITY_UNIT_MM = float(os.environ.get("GRIDFINITY_UNIT_MM", "42"))
    DEFAULT_LAYOUT_MARGIN_MM = float(os.environ.get("DEFAULT_LAYOUT_MARGIN_MM", "5"))
    SEGMENTATION_BACKEND = os.environ.get("SEGMENTATION_BACKEND", "opencv")


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    STORAGE_PATH = BASE_DIR / "tmp" / "test-storage"
    MIN_IMAGE_WIDTH = 1
    MIN_IMAGE_HEIGHT = 1
