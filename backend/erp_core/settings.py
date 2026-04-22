import os
import dj_database_url
import json
from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY ---
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-default-key-change-this-in-prod')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Dynamic ALLOWED_HOSTS
ALLOWED_HOSTS = ['*'] if DEBUG else [
    'api.erp.qmexai.com',
    'erp-e1ax.onrender.com',
    'api.qmexai.com',
    'localhost',
    '127.0.0.1'
]

# --- APP DEFINITION ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', 
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'api.apps.ApiConfig', 
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # TOP PRIORITY
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'api.middleware.UpdateLastActivityMiddleware',
]

ROOT_URLCONF = 'erp_core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'erp_core.wsgi.application'

# --- DATABASE ---
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL', 'postgres://postgres:postgres@localhost:5432/qmexai_db'),
        conn_max_age=600
    )
}

# --- CORS & CSRF (THE FIX) ---
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = DEBUG 

if not DEBUG:
    # Who can talk to this API
    CORS_ALLOWED_ORIGINS = [
        "https://erp.qmexai.com",
        "https://qmexaierp.netlify.app", 
        "https://qmexai.com",
        "https://www.qmexai.com",
    ]
    
    # Who is trusted for POST/PUT/DELETE requests
    CSRF_TRUSTED_ORIGINS = [
        "https://erp.qmexai.com",
        "https://api.erp.qmexai.com",
        "https://api.qmexai.com",
        "https://erp-e1ax.onrender.com"
    ]

# --- PRODUCTION SECURITY ---
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# --- STATIC FILES ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# --- AUTH & USER ---
AUTH_USER_MODEL = 'api.User'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'api.authentication.FirebaseAuthentication',
]

# --- REST FRAMEWORK CONFIG ---
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'api.authentication.FirebaseAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# --- INTERNATIONALIZATION ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'