import os
from pathlib import Path
from dotenv import load_dotenv
# Email_System
# Rajesh153@
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file from project root
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-dev-key-change-me")

DEBUG = False

allowed_hosts_env = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost")
ALLOWED_HOSTS = ['sendmail.pythonanywhere.com']

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "accounts",
    "campaigns",
    "footer",
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

ROOT_URLCONF = "email_system.urls"

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
                "django.contrib.messages.context_processors.messages",
                "footer.context_processors.footer_data",
            ],
        },
    },
]

WSGI_APPLICATION = "email_system.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"
    },
    {
        'NAME': 'accounts.validators.ComplexPasswordValidator',
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Karachi"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"

MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "2"))
MAX_RECIPIENTS_PER_CAMPAIGN = int(os.getenv("MAX_RECIPIENTS_PER_CAMPAIGN", "1000"))
MAX_EMAILS_PER_ACCOUNT_PER_DAY = int(os.getenv("MAX_EMAILS_PER_ACCOUNT_PER_DAY", "100"))
DEFAULT_SEND_BATCH_LIMIT = int(os.getenv("DEFAULT_SEND_BATCH_LIMIT", "20"))
DEFAULT_SEND_DELAY_SECONDS = int(os.getenv("DEFAULT_SEND_DELAY_SECONDS", "30"))

FIELD_ENCRYPTION_KEY = os.getenv("FIELD_ENCRYPTION_KEY", "")

# Security settings only for production
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    # Local development safety
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False