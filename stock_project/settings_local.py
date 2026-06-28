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
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')

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
