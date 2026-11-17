"""Main Flask application entry point for Deep Learning-Based Web Attack Detection & Early Warning System.

Features:
- Application Factory pattern (`create_app`)
- Modular Blueprint registration (API, Dashboard, Auth, Traffic, Detection, Alert)
- Centralized database initialization with Flask-SQLAlchemy
- Robust error handling for 400, 404, 405, 500 (JSON for API, HTML for web)
- Structured security-conscious logging (no credentials logged)
- Health endpoints (/health, /api/health)
"""

import os
import sys
import logging
from pathlib import Path
from flask import Flask, jsonify, render_template, request
from config import config_by_name, Config
from database.database import db
from routes import (
    auth_bp,
    dashboard_bp,
    traffic_bp,
    detection_bp,
    alert_bp,
    api_bp,
)

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("attack_detection_system")


def create_app(config_name: str = None) -> Flask:
    """Create and configure the Flask application."""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development").lower()

    app = Flask(__name__, template_folder="templates", static_folder="static")
    
    # Load configuration
    config_obj = config_by_name.get(config_name, Config)
    app.config.from_object(config_obj)

    # Ensure database folder exists for SQLite
    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if db_uri.startswith("sqlite:///"):
        db_file = db_uri.replace("sqlite:///", "")
        if db_file and db_file != ":memory:":
            db_path = Path(db_file)
            db_path.parent.mkdir(parents=True, exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    with app.app_context():
        try:
            from init_db import ensure_schema_upgrades
            ensure_schema_upgrades(db.engine)
        except Exception as e:
            logger.warning("Auto schema upgrade check: %s", e)

    # Register Blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(traffic_bp)
    app.register_blueprint(detection_bp)
    app.register_blueprint(alert_bp)

    # Request logging (safely omitting sensitive payloads)
    @app.before_request
    def log_incoming_request():
        if request.path.startswith("/api/"):
            logger.info("API Request: %s %s from %s", request.method, request.path, request.remote_addr)

    @app.after_request
    def log_response_status(response):
        if request.path.startswith("/api/"):
            logger.info("API Response: %s %s -> Status %d", request.method, request.path, response.status_code)
        return response

    # ========================================================================
    # Error Handlers (JSON for API calls, friendly templates for browser)
    # ========================================================================

    def wants_json() -> bool:
        return (
            request.path.startswith("/api/")
            or request.headers.get("Accept", "").startswith("application/json")
            or request.is_json
        )

    @app.errorhandler(400)
    def handle_bad_request(err):
        msg = getattr(err, "description", "Bad Request")
        if wants_json():
            return jsonify({"success": False, "error": msg}), 400
        return render_template("error.html", code=400, title="Bad Request", message=msg), 400

    @app.errorhandler(404)
    def handle_not_found(err):
        msg = "The requested resource was not found"
        if wants_json():
            return jsonify({"success": False, "error": msg}), 404
        return render_template("error.html", code=404, title="Page Not Found", message=msg), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(err):
        msg = f"Method {request.method} is not allowed for this endpoint"
        if wants_json():
            return jsonify({"success": False, "error": msg}), 405
        return render_template("error.html", code=405, title="Method Not Allowed", message=msg), 405

    @app.errorhandler(500)
    def handle_internal_error(err):
        logger.error("Internal Server Error on %s %s: %s", request.method, request.path, str(err))
        msg = "An internal server error occurred"
        if wants_json():
            return jsonify({"success": False, "error": msg}), 500
        return render_template("error.html", code=500, title="Server Error", message=msg), 500

    logger.info("Application configured successfully with '%s' settings.", config_name)
    return app


# Default application instance for WSGI servers and CLI
app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    logger.info("Starting Web Attack Detection System on http://127.0.0.1:%d (debug=%s)", port, debug)
    app.run(host="0.0.0.0", port=port, debug=debug)
