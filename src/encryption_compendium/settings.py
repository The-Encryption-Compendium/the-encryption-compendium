"""
Django settings for encryption_compendium project.

Generated by 'django-admin startproject' using Django 3.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import base64
import dotenv
import logging
import os
import secrets

from django.urls import reverse

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Read from .env file, if one exists
dotenv_path = os.path.join(BASE_DIR, ".env")
if os.path.exists(dotenv_path):
    dotenv.load_dotenv(dotenv_path)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
dev = os.getenv("DEVELOPMENT", "no").lower()
if dev == "yes":
    DEBUG = True
elif dev == "no":
    DEBUG = False
else:
    raise Exception(
        ("The DEVELOPMENT variable must be set to either 'yes' or " "'no'.")
    )

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = base64.b64encode(secrets.token_bytes()).decode("utf-8")
    else:
        raise Exception(
            (
                "DJANGO_SECRET_KEY must be explicitly set (as an environmental "
                "variable or in the .env file) when DEBUG is off."
            )
        )

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
if os.getenv("ALLOWED_HOSTS"):
    ALLOWED_HOSTS += os.getenv("ALLOWED_HOSTS").strip().replace(" ", "").split(",")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.forms",
    # django-compressor
    "compressor",
    # Apps developed in this repository
    "entries",
    "public_view",
    "research_assistant",
    "search",
    "users",
    "utils",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "encryption_compendium.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "encryption_compendium.wsgi.application"

# Allows custom widget templates
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASE_ENGINE = os.getenv("DATABASE_ENGINE", "sqlite3")
if DATABASE_ENGINE == "sqlite3":
    logging.info("Using SQLite3 database...")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
elif DATABASE_ENGINE == "postgres":
    logging.info("Using Postgres database...")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB"),
            "USER": os.getenv("POSTGRES_USER"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
            "HOST": os.getenv("DATABASE_HOST"),
            "PORT": os.getenv("DATABASE_HOST_PORT", "5432"),
        }
    }
else:
    raise Exception("DATABASE_ENGINE must be either sqlite3 or postgres.")

# Caching
# https://docs.djangoproject.com/en/stable/topics/cache/
backend = os.getenv("CACHE_BACKEND", "dummy")
if backend == "memcached":
    cache_location = os.getenv("MEMCACHED_HOSTS").split(",")
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.memcached.PyLibMCCache",
            "LOCATION": cache_location,
        }
    }
elif backend == "dummy":
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache",}}
else:
    raise Exception("CACHE_BACKEND must be 'dummy' or 'memcached'")

# Authentication options
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

MAX_PASSWORD_LENGTH = int(os.getenv("MAX_PASSWORD_LENGTH", 64))
MIN_PASSWORD_LENGTH = int(os.getenv("MIN_PASSWORD_LENGTH", 10))

AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]

AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": MIN_PASSWORD_LENGTH,},
    },
    {
        "NAME": "encryption_compendium.password_validation.MaximumLengthValidator",
        "OPTIONS": {"max_length": MAX_PASSWORD_LENGTH,},
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

# Login redirection

LOGIN_URL = "/research/login"
LOGIN_REDIRECT_URL = "/research/dashboard"
LOGOUT_REDIRECT_URL = "/research/login"

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Directory in which to store user files
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, os.pardir, "static")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "assets")]

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
)

### Compression settings for django-compressor
# COMPRESS_ENABLED: whether or not to compress files. Defaults to the
# opposite of DEBUG.
# COMPRESS_ENABLED = not DEBUG

# Filters to apply during compression
COMPRESS_FILTERS = {
    "css": [
        "compressor.filters.css_default.CssAbsoluteFilter",
        "compressor.filters.cssmin.CSSCompressorFilter",
    ],
}

### Email options
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "yes")
if EMAIL_USE_TLS == "yes":
    EMAIL_USE_TLS = True
elif EMAIL_USE_TLS == "no":
    EMAIL_USE_TLS = False
else:
    raise Exception("EMAIL_USE_TLS should be 'yes' or 'no'.")
