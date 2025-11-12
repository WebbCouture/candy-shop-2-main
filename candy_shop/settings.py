import os
from pathlib import Path
from django.contrib.messages import constants as messages
import dj_database_url
from dotenv import load_dotenv

# -------------------------------
# Build paths inside the project
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env (UTF-8 / UTF-16 fallback)
try:
    load_dotenv(BASE_DIR / ".env")
except Exception:
    pass

if not os.getenv("STRIPE_SECRET_KEY") or not os.getenv("STRIPE_PUBLIC_KEY"):
    try:
        load_dotenv(BASE_DIR / ".env", encoding="utf-16")
    except Exception:
        pass

# -------------------------------
# SECURITY SETTINGS
# -------------------------------
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'unsafe-dev-key')
DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true'

# ALLOWED_HOSTS from Heroku Config Vars (comma-separated)
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS]

# CSRF trusted origins built from ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in ALLOWED_HOSTS if host != "localhost"]

# Optional SSL settings for production on Heroku
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# -------------------------------
# Applications
# -------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
    'home',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
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

# -------------------------------
# Database
# -------------------------------
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# -------------------------------
# Password validation
# -------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------------------
# Internationalization
# -------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# -------------------------------
# Static files
# -------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'candy_shop' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# -------------------------------
# Messages tags
# -------------------------------
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -------------------------------
# Email
# -------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'webmaster@localhost'

# -------------------------------
# Auth URLs
# -------------------------------
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# -------------------------------
# Stripe
# -------------------------------
STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY", "")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")  # leave empty if not used
STRIPE_CURRENCY = os.environ.get("STRIPE_CURRENCY", "usd")
DOMAIN = os.environ.get("DOMAIN", "https://candy-shop-2-main-47a1afb34434.herokuapp.com")
