"""
Django settings for django_globus_app project.

Generated by 'django-admin startproject' using Django 3.2.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
from pathlib import Path

import logging
import os

log = logging.getLogger(__name__)

# Pull in environment specific settings
environment = os.environ.get("ENVIRONMENT", "local")
if environment == "local":
    try:
        from .local import *
    except ImportError:
        expected_path = Path(__file__).resolve().parent / "local.py"
        log.warning(f"You should create a file for your secrets at {expected_path}")
elif environment == "production":
    try:
        from .production import *
    except ImportError:
        expected_path = Path(__file__).resolve().parent / "production.py"
        log.warning(f"You should create a file for your secrets at {expected_path}")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# This is a general Django setting if views need to redirect to login
# https://docs.djangoproject.com/en/3.2/ref/settings/#login-url
LOGIN_URL = "/login/globus"

# This dictates which scopes will be requested on each user login
SOCIAL_AUTH_GLOBUS_SCOPE = [
    "urn:globus:auth:scope:search.api.globus.org:all",
]

ALLOWED_HOSTS = ["*"]


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_globus_app",
    "globus_portal_framework",
    "social_django",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "globus_portal_framework.middleware.ExpiredTokenMiddleware",
    "globus_portal_framework.middleware.GlobusAuthExceptionMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
]

# Authentication backends setup OAuth2 handling and where user data should be
# stored
AUTHENTICATION_BACKENDS = [
    "globus_portal_framework.auth.GlobusOpenIdConnect",
    "django.contrib.auth.backends.ModelBackend",
]

ROOT_URLCONF = "django_globus_app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "globus_portal_framework.context_processors.globals",
            ],
        },
    },
]

WSGI_APPLICATION = "django_globus_app.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LOGGING = {
    "version": 1,
    "handlers": {
        "stream": {"level": "DEBUG", "class": "logging.StreamHandler"},
    },
    "loggers": {
        "django": {"handlers": ["stream"], "level": "INFO"},
        "django_globus_app": {"handlers": ["stream"], "level": "DEBUG"},
    },
}

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATICFILES_DIRS = [BASE_DIR / "staticfiles"]
STATIC_ROOT = BASE_DIR / "static"
STATIC_URL = "/static/"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Import Globus Search specific settings
try:
    from .search import *
except ImportError:
    expected_path = Path(__file__).resolve().parent / "search.py"
    log.warning(f"You should create a file for your search settings at {expected_path}")
