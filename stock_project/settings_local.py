"""
Local Django settings for stock_project.

This module imports all environment-independent base settings from
stock_project.settings and overrides environment-specific values from
a local .env file. It is intended for local development only.
"""

import os

from dotenv import load_dotenv

from stock_project.settings import *  # noqa: F401,F403

# Load environment variables from the project .env file.
# The file is expected to be at the project root (one level above this file).
load_dotenv(dotenv_path=BASE_DIR / '.env')  # noqa: F405

# Environment-specific Django settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key-change-in-production')
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# CSRF trusted origins: use explicit env value or derive from ALLOWED_HOSTS
csrf_origins_env = os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in csrf_origins_env if origin.strip()]
if not CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS = [f"http://{host.strip()}" for host in ALLOWED_HOSTS if host.strip() not in ('*', '')]

# Trust forwarded headers from nginx reverse proxy
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Database settings loaded from environment variables
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'stock_db'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5433'),
    }
}
