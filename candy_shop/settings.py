import os
from pathlib import Path
from django.contrib.messages import constants as messages
import dj_database_url
from dotenv import load_dotenv

# ===============================
# Paths & .env
# ===============================
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env (UTF-8 first, fallback to UTF-16 if keys are missing)
try:
    load_dotenv(BASE_DIR / ".env")
except Exception:
    pass

if not os.getenv("STRIPE_SECRET_KEY") or not os.getenv("STRIPE_PUBLIC_KEY"):
    try:
        load_dotenv(BASE_DIR / ".env", encoding="utf-16")
    except Exception:
        pass

# ===============================
# Security / Debug
# ===============================
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'unsafe-dev-key')
DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true'

# Allowed hosts (comma-separated in env). Good defaults for local dev.
ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if h.strip()
]

# CSRF Trusted Origins:
# - If CSRF_TRUSTED_ORIGINS is set in env, use it.
# - Otherwise: sensible local defaults + herokuapp hosts from ALLOWED_HOSTS.
_csrf_from_env = [
    u.strip() for u in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')
    if u.strip()
]
CSRF_TRUSTED_ORIGINS = _csrf_from_env or [
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
] + [f"https://{h}" for h in ALLOWED_HOSTS if h.endswith("herokuapp.com")]

# Enforce HTTPS only in production (Heroku)
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# Behind Heroku proxy
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# HSTS can be enabled once everything works in production:
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# ===============================
# Applications
# ===============================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
    'home',
    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # Important for static files on Heroku
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'candy_shop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'candy_shop' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'main.context_processors.cart_item_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'candy_shop.wsgi.application'

# ===============================
# Database (Postgres if DATABASE_URL exists; otherwise SQLite locally)
# ===============================
if "DATABASE_URL" in os.environ and os.environ["DATABASE_URL"]:
    DATABASES = {
        "default": dj_database_url.config(
            conn_max_age=600,
            ssl_require=True,  # only for external/Postgres DB
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ===============================
# Password validation
# ===============================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ===============================
# Internationalization
# ===============================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Stockholm'
USE_I18N = True
USE_TZ = True

# ===============================
# Static / Media (WhiteNoise)
# ===============================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'candy_shop' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ===============================
# Messages tags
# ===============================
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===============================
# Email (dev default)
# ===============================
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'webmaster@localhost'

# ===============================
# Auth URLs
# ===============================
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# ===============================
# Stripe
# ===============================
STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY", "")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")  # leave empty if not used
STRIPE_CURRENCY = os.environ.get("STRIPE_CURRENCY", "usd")  # match your $ display
DOMAIN = os.environ.get("DOMAIN", "https://candy-shop-2-main-47a1afb34434.herokuapp.com")
