"""
Bhasha Shiksha Setu - Configuration
"""

import os
from pathlib import Path

from dotenv import load_dotenv


# ============================================================
# PROJECT PATHS
# ============================================================

# backend/config.py
#       ↓
# backend/
#       ↓
# project root

BASE_DIR = Path(__file__).resolve().parent.parent


# Load .env from project root
load_dotenv(BASE_DIR / ".env")


# ============================================================
# BOOLEAN HELPER
# ============================================================

def _bool(value, default=False):
    if value is None:
        return default

    return str(value).strip().lower() in (
        "1",
        "true",
        "yes",
        "on"
    )


# ============================================================
# CONFIGURATION
# ============================================================

class Config:

    # --------------------------------------------------------
    # Flask
    # --------------------------------------------------------

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "change-this-secret-key-in-production"
    )

    DEBUG = _bool(
        os.getenv("DEBUG"),
        False
    )


    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------

    DEFAULT_DATABASE = (
        "sqlite:///"
        + str(BASE_DIR / "bhasha_shiksha_setu.db")
    )

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        DEFAULT_DATABASE
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True
    }


    # --------------------------------------------------------
    # Authentication
    # --------------------------------------------------------

    JWT_EXPIRY_HOURS = int(
        os.getenv(
            "TOKEN_EXPIRY_HOURS",
            "24"
        )
    )

    LOGIN_MAX_ATTEMPTS = 5

    LOGIN_LOCKOUT_MINUTES = 15


    # --------------------------------------------------------
    # Uploads
    # --------------------------------------------------------

    MAX_UPLOAD_MB = int(
        os.getenv(
            "MAX_UPLOAD_MB",
            "250"
        )
    )

    MAX_CONTENT_LENGTH = (
        MAX_UPLOAD_MB * 1024 * 1024
    )


    # --------------------------------------------------------
    # IMPORTANT:
    # Your current project has uploads/ at ROOT level.
    #
    # project/
    # ├── uploads/
    # └── backend/
    #
    # --------------------------------------------------------

    UPLOAD_DIR = os.getenv(
        "UPLOAD_DIR",
        str(BASE_DIR / "uploads")
    )


    # --------------------------------------------------------
    # CORS
    # --------------------------------------------------------

    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS",
        "*"
    )


    # --------------------------------------------------------
    # AI
    # --------------------------------------------------------

    AI_PROVIDER = os.getenv(
        "AI_PROVIDER",
        "demo"
    )

    AI_API_KEY = os.getenv(
        "AI_API_KEY",
        ""
    )

    AI_MODEL = os.getenv(
        "AI_MODEL",
        "gpt-4o-mini"
    )

    AI_BASE_URL = os.getenv(
        "AI_BASE_URL",
        "https://api.openai.com/v1"
    )


    # --------------------------------------------------------
    # Video dubbing
    # --------------------------------------------------------

    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
    VIDEO_DUBBING_PROVIDER = os.getenv("VIDEO_DUBBING_PROVIDER", "elevenlabs")


    # --------------------------------------------------------
    # Translation
    # --------------------------------------------------------

    TRANSLATION_PROVIDER = os.getenv(
        "TRANSLATION_PROVIDER",
        "demo"
    )


    # --------------------------------------------------------
    # Text To Speech
    # --------------------------------------------------------

    TTS_PROVIDER = os.getenv(
        "TTS_PROVIDER",
        "browser"
    )

    TTS_URL = os.getenv(
        "TTS_URL",
        ""
    )

    TTS_API_KEY = os.getenv(
        "TTS_API_KEY",
        ""
    )


    # --------------------------------------------------------
    # Speech To Text
    # --------------------------------------------------------

    STT_URL = os.getenv(
        "STT_URL",
        ""
    )

    STT_API_KEY = os.getenv(
        "STT_API_KEY",
        ""
    )


    # --------------------------------------------------------
    # FRONTEND
    #
    # Kept here because the original project contains
    # frontend/ as well.
    # --------------------------------------------------------

    FRONTEND_DIR = BASE_DIR / "frontend"


    # --------------------------------------------------------
    # ADMIN DASHBOARD
    #
    # This is the important part for your current structure.
    #
    # project/
    # ├── admin/
    # │   ├── admin.html
    # │   ├── admin.css
    # │   └── admin.js
    # │
    # └── backend/
    #     └── config.py
    # --------------------------------------------------------

    ADMIN_DIR = BASE_DIR / "admin"


    # --------------------------------------------------------
    # Default Admin Account
    # --------------------------------------------------------

    ADMIN_NAME = os.getenv(
        "ADMIN_NAME",
        "Administrator"
    )

    ADMIN_EMAIL = os.getenv(
        "ADMIN_EMAIL",
        "admin@bhasha.setu"
    )

    ADMIN_PASSWORD = os.getenv(
        "ADMIN_PASSWORD",
        "Admin@123"
    )


    # --------------------------------------------------------
    # Demo Data
    # --------------------------------------------------------

    SEED_DEMO = _bool(
        os.getenv("SEED_DEMO"),
        True
    )


    # --------------------------------------------------------
    # Safe public settings
    # --------------------------------------------------------

    @staticmethod
    def public_settings():

        return {
            "ai_provider": os.getenv(
                "AI_PROVIDER",
                "demo"
            ),

            "ai_model": os.getenv(
                "AI_MODEL",
                "gpt-4o-mini"
            ),

            "translation_provider": os.getenv(
                "TRANSLATION_PROVIDER",
                "demo"
            )
    }
