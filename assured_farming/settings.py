# assured_farming/settings.py
import os
from pathlib import Path
import environ
import dj_database_url
from datetime import timedelta

# -------------------------------------------------------------------
# BASE CONFIGURATION
# -------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)

# Load environment variables from .env file at project root (dev only)
environ.Env.read_env(env_file=os.path.join(BASE_DIR, '.env'))

# -------------------------------------------------------------------
# SECURITY (use envs; supports both local .env and production)
# -------------------------------------------------------------------

# SECRET: prefer SECRET_KEY for prod (Render), fallback to DJANGO_SECRET_KEY for dev
SECRET_KEY = os.environ.get('SECRET_KEY') or env('DJANGO_SECRET_KEY', default='dev-secret')

# DEBUG: prefer explicit DEBUG env in production; keep DJANGO_DEBUG for local dev
DEBUG = os.environ.get('DEBUG', os.environ.get('DJANGO_DEBUG', "True")) in ("True", "true", "1")

# ALLOWED HOSTS (comma separated in env)
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', "*").split(",")

# -------------------------------------------------------------------
# APPLICATIONS
# -------------------------------------------------------------------

INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'drf_spectacular',
    'corsheaders',

    # Local apps
    'core',
    'accounts',
    'marketplace',
    'contracts',
    'payments',
    'notifications',
    'analytics',
]

# -------------------------------------------------------------------
# TEMPLATES
# -------------------------------------------------------------------

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# -------------------------------------------------------------------
# MIDDLEWARE
# -------------------------------------------------------------------

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',   # Must be placed before CommonMiddleware
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # serve static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.RequestAuditMiddleware',
]

# -------------------------------------------------------------------
# URLS / WSGI
# -------------------------------------------------------------------

ROOT_URLCONF = 'assured_farming.urls'
WSGI_APPLICATION = 'assured_farming.wsgi.application'

# -------------------------------------------------------------------
# DATABASE CONFIGURATION
# -------------------------------------------------------------------
# Prefer DATABASE_URL (Render injects this). Fallback to USE_POSTGRESQL / POSTGRES_* for dev.
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    # Use SQLite for development unless explicitly opting into POSTGRES locally
    USE_POSTGRESQL = env.bool('USE_POSTGRESQL', default=False)

    if USE_POSTGRESQL:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': env('POSTGRES_DB', default='assured_farming'),
                'USER': env('POSTGRES_USER', default='postgres'),
                'PASSWORD': env('POSTGRES_PASSWORD', default='postgres'),
                'HOST': env('POSTGRES_HOST', default='db'),
                'PORT': env('POSTGRES_PORT', default='5432'),
            }
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }

# -------------------------------------------------------------------
# AUTH / USERS
# -------------------------------------------------------------------

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------------------------------------------------------
# INTERNATIONALIZATION
# -------------------------------------------------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# -------------------------------------------------------------------
# STATIC & MEDIA FILES
# -------------------------------------------------------------------

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -------------------------------------------------------------------
# EMAIL BACKEND (DEV)
# -------------------------------------------------------------------

EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')

# -------------------------------------------------------------------
# REDIS / CELERY
# -------------------------------------------------------------------

REDIS_URL = env('REDIS_URL', default='redis://localhost:6379/0')

CELERY_BROKER_URL = env('CELERY_BROKER_URL', default=REDIS_URL)
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default=REDIS_URL)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
# Run tasks eagerly in local development unless explicitly disabled
CELERY_TASK_ALWAYS_EAGER = env.bool('CELERY_TASK_ALWAYS_EAGER', default=True)

# -------------------------------------------------------------------
# REST FRAMEWORK / DRF SPECTACULAR
# -------------------------------------------------------------------

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20,
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Assured Farming API',
    'DESCRIPTION': 'Platform for transparent contract farming, escrow payments, and analytics.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# -------------------------------------------------------------------
# SIMPLE JWT SETTINGS
# -------------------------------------------------------------------

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# -------------------------------------------------------------------
# CORS SETTINGS (for React Frontend)
# -------------------------------------------------------------------

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Optional for development only:
CORS_ALLOW_CREDENTIALS = True

# -------------------------------------------------------------------
# LOGGING
# -------------------------------------------------------------------

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
