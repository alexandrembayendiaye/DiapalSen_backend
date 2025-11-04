"""
Paramètres pour l'environnement de développement
"""

import os
from .base import *
from decouple import config

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Database - PostgreSQL pour le développement
# Database - PostgreSQL pour le développement
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

# Vérification que le .env est bien configuré
if not all(
    [
        config("DB_NAME"),
        config("DB_USER"),
        config("DB_PASSWORD"),
    ]
):
    raise ValueError(
        "❌ Fichier .env manquant ou incomplet ! Vérifiez DB_NAME, DB_USER, DB_PASSWORD"
    )

# CORS settings pour le développement (React frontend)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

# Cache (simple pour le développement)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Email backend pour le développement (console)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Security settings (relaxées pour le développement)
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Debug toolbar (temporairement désactivé)
# if DEBUG:
#     INSTALLED_APPS += ['debug_toolbar']
#     MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
#     INTERNAL_IPS = ['127.0.0.1']
# Créer le dossier logs s'il n'existe pas
import pathlib

log_dir = BASE_DIR / "logs"
pathlib.Path(log_dir).mkdir(exist_ok=True)

print("🚀 Settings de développement chargés")
