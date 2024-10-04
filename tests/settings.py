import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = "django-mail-analytics"

ALLOWED_HOSTS = ["*"]

# Application definition
INSTALLED_APPS = [
    "tests",
    "django_mail_analytics",
]

INSTALLED_APPS += [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.common.CommonMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

MEDIA_ROOT = os.path.join(BASE_DIR, "tests/media/")
MEDIA_URL = "/media/"

STATIC_ROOT = os.path.join(BASE_DIR, "tests/static/")
STATIC_URL = "/static/"

ROOT_URLCONF = "tests.urls"

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
MAIL_ANALYTICS = {
    "DOMAIN": "localhost",
    "SCHEME": "http",
    # "SALT": "my-salt", #comment to use global SECRET_KEY instead
    "LENGTH": 6,  # minimal length of encoded id
}
