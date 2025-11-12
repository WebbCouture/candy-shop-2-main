import os
from pathlib import Path
from django.contrib.messages import constants as messages  # for message tags
import dj_database_url  # for Heroku Postgres support

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ---- Load .env (handles your BOM/UTF-16 case) ----
from dotenv import load_dotenv
# Try standard UTF-8 first (don’t crash if encoding is wrong)
try:
    load_dotenv(BASE_DIR / ".env")
except Exception:
    pass
# Fallback for .env saved as UTF-16 or with BOM (prevents UnicodeDecodeError)
if not os.getenv("STRIPE_SECRET_KEY") or not os.getenv("STRIPE_PUBLIC_KEY"):
    try:
        load_dotenv(BASE_DIR / ".env", encoding="utf-16")
    except Exception:
        pass
# ---------------------------------------------------

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-wxs3%36rv84(791g@%v-+o8lt6w_n*6hy(jdbver@ft0(_0b)c'
)


DEBUG = False  # Change this to True for local dev if needed


if "DJANGO_DEBUG" in os.environ:
    DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"


ALLOWED_HOSTS = [
    'candyshop-demo-bf556706b864.herokuapp.com',  # Heroku domain
    'localhost',  # Local development
    '127.0.0.1'   # Localhost IP
]

# Trust these origins for CSRF (needed for password reset and other POST forms)
CSRF_TRUSTED_ORIGINS = [
    'https://candyshop-demo-bf556706b864.herokuapp.com',
    'http://localhost',
    'http://127.0.0.1',
]

# Application definition
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

# Database configuration (use Heroku Postgres or SQLite depending on the environment)
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

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'candy_shop' / 'static'] 
STATIC_ROOT = BASE_DIR / 'staticfiles'  

# Use WhiteNoise to serve static files in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Messages framework tags for bootstrap compatibility
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Email backend for development ---
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'webmaster@localhost'

# Login URLs (use names instead of hardcoded paths to avoid typos)
LOGIN_URL = 'login'                # was '/account/login/' — fixed
LOGIN_REDIRECT_URL = 'home'        # redirect after login
LOGOUT_REDIRECT_URL = 'home'       # redirect after logout

# ============================
# Stripe / payments (added)
# ============================
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "") 
STRIPE_CURRENCY = os.getenv("STRIPE_CURRENCY", "usd")  
DOMAIN = os.getenv("DOMAIN", "http://127.0.0.1:8000")  


