import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "database" / "app.db"


class Config:
    """Base configuration for Flask application."""

    # Security: Secret key for session management and CSRF protection
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

    # Database: SQLite database URL pointing to database/app.db
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security: Cookie and Session hardening
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("FLASK_ENV") == "production"

    # Directory Paths
    DATA_DIR = os.getenv("DATA_DIR", str(BASE_DIR / "data" / "raw"))
    PROCESSED_DIR = os.getenv("PROCESSED_DIR", str(BASE_DIR / "data" / "processed"))
    TEST_DIR = os.getenv("TEST_DIR", str(BASE_DIR / "data" / "test"))
    MODELS_DIR = os.getenv("MODELS_DIR", str(BASE_DIR / "models"))

    # TensorFlow Environment Variables
    TF_CPP_MIN_LOG_LEVEL = os.getenv("TF_CPP_MIN_LOG_LEVEL", "2")
    TF_ENABLE_ONEDNN_OPTS = os.getenv("TF_ENABLE_ONEDNN_OPTS", "0")


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True


class TestingConfig(Config):
    """Testing configuration with in-memory database."""

    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    SESSION_COOKIE_SECURE = True


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
