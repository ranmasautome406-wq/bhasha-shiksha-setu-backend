"""
Bhasha Shiksha Setu - Backend Application

Flask application factory for the backend API.

The frontend is deployed separately, so this file does NOT serve
HTML/CSS/JS files. It only provides the backend API.
"""

import os

from flask import Flask, jsonify, request
from flask_cors import CORS

from backend.config import Config
from backend.database import init_db


def create_app(config_object=Config):
    """
    Create and configure the Flask application.
    """

    app = Flask(__name__, static_folder=None)

    # ---------------------------------------------------------
    # Configuration
    # ---------------------------------------------------------
    app.config.from_object(config_object)

    # Database configuration
    if app.config.get("SQLALCHEMY_DATABASE_URI"):
        app.config["SQLALCHEMY_DATABASE_URI"] = (
            app.config["SQLALCHEMY_DATABASE_URI"]
        )

    # Upload directory
    app.config["UPLOAD_DIR"] = os.getenv(
        "UPLOAD_DIR",
        app.config.get("UPLOAD_DIR", "uploads")
    )

    # Make sure upload directory exists
    os.makedirs(app.config["UPLOAD_DIR"], exist_ok=True)

    # ---------------------------------------------------------
    # CORS
    # ---------------------------------------------------------
    cors_origins = app.config.get("CORS_ORIGINS", "*")

    if isinstance(cors_origins, str):
        cors_origins = [
            origin.strip()
            for origin in cors_origins.split(",")
            if origin.strip()
        ]

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": cors_origins or "*"
            }
        },
        allow_headers=[
            "Content-Type",
            "Authorization",
            "X-Guest-Id"
        ],
        methods=[
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
            "OPTIONS"
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
            "X-XSS-Protection",
            "1; mode=block"
        )

        response.headers.setdefault(
            "Referrer-Policy",
            "same-origin"
        )

        return response

    # ---------------------------------------------------------
    # Backend home
    # ---------------------------------------------------------
    @app.get("/")
    def backend_home():
        return jsonify({
            "success": True,
            "message": "Bhasha Shiksha Setu Backend is running",
            "project": "Bhasha Shiksha Setu",
            "version": "1.0",
            "type": "REST API",
            "api": "/api",
            "health": "/api/health"
        })

    # ---------------------------------------------------------
    # API information
    # ---------------------------------------------------------
    @app.get("/api")
    def api_home():
        return jsonify({
            "success": True,
            "message": "Bhasha Shiksha Setu API",
            "project": "Bhasha Shiksha Setu",
            "endpoints": {
                "health": "/api/health",
                "authentication": "/api/auth",
                "student": "/api/student",
                "teacher": "/api/teacher",
                "tutor": "/api/tutor",
                "content": "/api/content",
                "voice": "/api/voice",
                "admin": "/api/admin"
            }
        })

    # ---------------------------------------------------------
    # Health check
    # ---------------------------------------------------------
    @app.get("/api/health")
    def health_check():
        return jsonify({
            "success": True,
            "status": "healthy",
            "project": "Bhasha Shiksha Setu",
            "backend": "online"
        })

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
        voice
    )

    blueprints = [
        auth.bp,
        content.bp,
        student.bp,
        teacher.bp,
        tutor.bp,
        voice.bp,
        admin.bp
    ]

    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    # ---------------------------------------------------------
    # 404 handler
    # ---------------------------------------------------------
    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith("/api/"):
            return jsonify({
                "success": False,
                "message": "API endpoint not found.",
                "path": request.path
            }), 404

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
        if request.path.startswith("/api/"):
            return jsonify({
                "success": False,
                "message": "Method not allowed for this API endpoint.",
                "path": request.path
            }), 405

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
        max_mb = (
            app.config.get("MAX_CONTENT_LENGTH", 10 * 1024 * 1024)
            / 1024
            / 1024
        )

        return jsonify({
            "success": False,
            "message": (
                f"Upload too large. Maximum allowed size is "
                f"{max_mb:.1f} MB."
            )
        }), 413

    # ---------------------------------------------------------
    # Global exception handler
    # ---------------------------------------------------------
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.exception(
            "Unhandled backend error: %s",
            error
        )

        return jsonify({
            "success": False,
            "message": "Something went wrong. Please try again."
        }), 500

    # ---------------------------------------------------------
    # Initialize database
    # ---------------------------------------------------------
    init_db(app)

    return app


# -------------------------------------------------------------
# WSGI application
# -------------------------------------------------------------
app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=app.config.get("DEBUG", False)
    )
