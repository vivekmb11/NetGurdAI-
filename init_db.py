"""Database initialization script for Deep Learning Attack Detection System.

Usage:
    python init_db.py

Function:
- Verifies and creates database directory if missing.
- Initializes database/app.db with all required tables:
    * users
    * websites
    * traffic
    * detections
    * alerts
- Safe: Does NOT drop or delete existing database tables.
"""

import sys
import logging
from pathlib import Path
from sqlalchemy import inspect
from app import create_app
from database.database import db
from database.models import User, Website, Traffic, Detection, Alert

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
logger = logging.getLogger("init_db")


def init_database() -> bool:
    """Initialize database and create all required tables."""
    app = create_app()
    with app.app_context():
        db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
        logger.info("Connecting to database URI: %s", db_uri)

        # Ensure database directory exists
        if db_uri.startswith("sqlite:///"):
            db_path_str = db_uri.replace("sqlite:///", "")
            if db_path_str and db_path_str != ":memory:":
                db_path = Path(db_path_str)
                db_path.parent.mkdir(parents=True, exist_ok=True)
                if db_path.exists():
                    logger.info("Database file exists at '%s' (preserving data).", db_path)
                else:
                    logger.info("Creating new database file at '%s'...", db_path)

        # Create all tables safely
        logger.info("Creating database tables if not present...")
        db.create_all()

        # Migrate existing schema if any columns are missing (Phase 13 updates)
        ensure_schema_upgrades(db.engine)

        # Verify created tables using SQLAlchemy inspector
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        logger.info("Found tables in database: %s", existing_tables)

        required_tables = ["users", "websites", "traffic", "detections", "alerts"]
        missing_tables = [t for t in required_tables if t not in existing_tables]

        if missing_tables:
            logger.error("Database initialization incomplete. Missing tables: %s", missing_tables)
            return False

        logger.info("[OK] All database tables successfully initialized and verified:")
        for tbl in required_tables:
            columns = [col["name"] for col in inspector.get_columns(tbl)]
            logger.info("  - Table '%s' with columns: %s", tbl, columns)

        return True


def ensure_schema_upgrades(engine) -> None:
    """Ensure database schema is up-to-date with new columns without dropping data."""
    from sqlalchemy import text
    inspector = inspect(engine)
    if "traffic" in inspector.get_table_names():
        existing_cols = {col["name"] for col in inspector.get_columns("traffic")}
        new_columns = [
            ("client_id", "VARCHAR(100)"),
            ("ip_address", "VARCHAR(45)"),
            ("user_agent", "VARCHAR(500)"),
            ("method", "VARCHAR(10) DEFAULT 'GET'"),
            ("path", "VARCHAR(255) DEFAULT '/'"),
            ("traffic_type", "VARCHAR(30) DEFAULT 'UNKNOWN'"),
            ("classification_confidence", "FLOAT"),
            ("risk_level", "VARCHAR(20) DEFAULT 'LOW'"),
            ("response_time", "FLOAT"),
            ("request_frequency", "FLOAT"),
            ("source", "VARCHAR(100) DEFAULT 'telemetry'"),
        ]
        with engine.connect() as conn:
            for col_name, col_type in new_columns:
                if col_name not in existing_cols:
                    logger.info("Migrating table 'traffic': adding column '%s' (%s)", col_name, col_type)
                    conn.execute(text(f"ALTER TABLE traffic ADD COLUMN {col_name} {col_type}"))
            conn.commit()


if __name__ == "__main__":
    success = init_database()
    if success:
        print("\nDatabase initialization complete. All required tables are ready.\n")
        sys.exit(0)
    else:
        print("\nDatabase initialization failed!\n", file=sys.stderr)
        sys.exit(1)
