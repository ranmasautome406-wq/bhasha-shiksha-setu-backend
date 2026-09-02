"""
Bhasha Shiksha Setu - Flask Backend
"""

import os
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from backend.config import Config
from backend.database import init_db


def create_app(config_object=Config):
    app = Flask(__name__, static_folder=None)

    # ---------------------------------------------------------
    # Configuration
    # ---------------------------------------------------------
    app.config.from_object(config_object)

    # Environment overrides
    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        app.config.get("SECRET_KEY", "change-this-secret-key")
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        app.config["SQLALCHEMY_DATABASE_URI"]
    )

    app.config["UPLOAD_DIR"] = os.getenv(
        "UPLOAD_DIR",
        str(app.config["UPLOAD_DIR"])
    )

    # ---------------------------------------------------------
    # CORS
    # ---------------------------------------------------------
    cors_origins = os.getenv(
        "CORS_ORIGINS",
        app.config.get("CORS_ORIGINS", "*")
    )

    if cors_origins == "*":
        CORS(
            app,
            resources={r"/api/*": {"origins": "*"}},
            allow_headers=[
                "Content-Type",
                "Authorization",
                "X-Guest-Id"
            ]
        )
    else:
        origins = [
            item.strip()
            for item in cors_origins.split(",")
            if item.strip()
        ]

        CORS(
            app,
            resources={r"/api/*": {"origins": origins}},
            allow_headers=[
                "Content-Type",
                "Authorization",
                "X-Guest-Id"
            ]
        )

    # ---------------------------------------------------------
    # Security headers
    # ---------------------------------------------------------
    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault(
            "X-Content-Type-Options",
            "nosniff"
        )

        response.headers.setdefault(
            "X-Frame-Options",
            "SAMEORIGIN"
        )

        response.headers.setdefault(
            "Referrer-Policy",
            "same-origin"
        )

        return response

    # ---------------------------------------------------------
    # Register API blueprints
    # ---------------------------------------------------------
    from backend.routes import (
        admin,
        auth,
        content,
        student,
        teacher,
        tutor,
        voice,
    )

    blueprints = [
        auth.bp,
        content.bp,
        student.bp,
        teacher.bp,
        tutor.bp,
        voice.bp,
        admin.bp,
        admin.alias_bp,
    ]

    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    # ---------------------------------------------------------
    # ADMIN DASHBOARD
    #
    # Project structure:
    #
    # project/
    # ├── admin/
    # │   ├── admin.html
    # │   ├── admin.css
    # │   └── admin.js
    # └── backend/
    #     └── app.py
    # ---------------------------------------------------------

    admin_dir = Path(app.config["ADMIN_DIR"])

    @app.route("/admin")
    @app.route("/admin/")
    def admin_dashboard():
        return send_from_directory(
            str(admin_dir),
            "admin.html"
        )

    @app.route("/admin/<path:filename>")
    def admin_static_files(filename):
        # Prevent API paths from being treated as static files
        if filename.startswith("api/"):
            return jsonify({
                "success": False,
                "message": "Endpoint not found."
            }), 404

        requested_file = admin_dir / filename

        # Security: do not allow files outside admin directory
        try:
            requested_file.resolve().relative_to(
                admin_dir.resolve()
            )
        except ValueError:
            return jsonify({
                "success": False,
                "message": "Invalid file path."
            }), 400

        if requested_file.is_file():
            return send_from_directory(
                str(admin_dir),
                filename
            )

        return jsonify({
            "success": False,
            "message": "Admin file not found.",
            "file": filename
        }), 404

    # ---------------------------------------------------------
    # Backend health endpoint
    # ---------------------------------------------------------
    @app.get("/api/health")
    def health():
        return jsonify({
            "success": True,
            "status": "healthy",
            "message": "Bhasha Shiksha Setu backend is running.",
            "project": "Bhasha Shiksha Setu",
            "admin": "/admin"
        })

    # ---------------------------------------------------------
    # Backend root
    # ---------------------------------------------------------
    @app.get("/")
    def backend_home():
        return jsonify({
            "success": True,
            "message": "Bhasha Shiksha Setu backend is running.",
            "project": "Bhasha Shiksha Setu",
            "admin_dashboard": "/admin",
            "health": "/api/health"
        })

    # ---------------------------------------------------------
    # Uploaded media
    # ---------------------------------------------------------
    @app.route("/uploads/<path:filename>")
    def uploaded_media(filename):
        upload_dir = Path(app.config["UPLOAD_DIR"]).resolve()
        requested = (upload_dir / filename).resolve()
        try:
            requested.relative_to(upload_dir)
        except ValueError:
            return jsonify({"success": False, "message": "Invalid file path."}), 400
        if not requested.is_file():
            return jsonify({"success": False, "message": "File not found."}), 404
        return send_from_directory(str(upload_dir), filename)

    # ---------------------------------------------------------
    # 404 handler
    # ---------------------------------------------------------
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "message": "Backend route not found.",
            "path": request.path
        }), 404

    # ---------------------------------------------------------
    # 405 handler
    # ---------------------------------------------------------
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "message": "Method not allowed.",
            "path": request.path
        }), 405

    # ---------------------------------------------------------
    # 413 handler
    # ---------------------------------------------------------
    @app.errorhandler(413)
    def request_too_large(error):
        maximum = app.config.get(
            "MAX_CONTENT_LENGTH",
            50 * 1024 * 1024
        )

        maximum_mb = maximum / (1024 * 1024)

        return jsonify({
            "success": False,
            "message": f"Upload too large. Maximum size is {maximum_mb:.0f} MB."
        }), 413

    # ---------------------------------------------------------
    # General error handler
    # ---------------------------------------------------------
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.exception(
            "Unhandled server error: %s",
            error
        )

        return jsonify({
            "success": False,
            "message": "Something went wrong on the server."
        }), 500

    # ---------------------------------------------------------
    # Database
    # ---------------------------------------------------------
    init_db(app)

    return app


# -------------------------------------------------------------
# Create application
# -------------------------------------------------------------
app = create_app()


# -------------------------------------------------------------
# Local development
# -------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=app.config.get("DEBUG", False)
        )
