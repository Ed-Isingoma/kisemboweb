from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-o-!nknvrvdcsej^uj-j4xdd7poo$g0)g8o+vy0$_ia^36k2x-c'


DEBUG = False
# this is a windows thing
# NPM_BIN_PATH = "C:/Program Files/nodejs/npm.cmd"


CSRF_TRUSTED_ORIGINS = ["https://kisemboweb.onrender.com", "https://kisemboacademy.com"]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'web',
    'corsheaders',
    'tailwind',
    'theme',
    'django.contrib.sites',
    'allauth', 'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
  ] 

AUTHENTICATION_BACKENDS = [
  'allauth.account.auth_backends.AuthenticationBackend',
]


GOOGLE_OAUTH2_CLIENT_ID     = os.getenv('GOOGLE_OAUTH2_CLIENT_ID')
GOOGLE_OAUTH2_CLIENT_SECRET = os.getenv('GOOGLE_OAUTH2_CLIENT_SECRET')
GOOGLE_OAUTH2_REDIRECT_URI  = os.getenv('GOOGLE_OAUTH2_REDIRECT_URI')
SITE_ID = 2


TAILWIND_APP_NAME = 'theme' 

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    ALLOWED_HOSTS = ["*"]
    INSTALLED_APPS += ['django_browser_reload']
    MIDDLEWARE += ['django_browser_reload.middleware.BrowserReloadMiddleware']
else:
    CORS_ALLOWED_ORIGINS = [
        "https://kisemboacademy.com",
        "https://kisemboweb.onrender.com"
    ]
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_DATABASE'),
            'USER': os.getenv('DB_USERNAME'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOSTNAME'),
            'PORT': os.getenv('DB_PORT'),
        }
    }
    ALLOWED_HOSTS = ["kisemboweb.onrender.com", "kisemboacademy.com"]



ROOT_URLCONF = 'kisemboweb.urls'

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

INTERNAL_IPS = [
    "127.0.0.1",
]

WSGI_APPLICATION = 'kisemboweb.wsgi.application'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True

USE_TZ = True

FLW_SECRET_KEY = os.getenv('FLW_SECRET_KEY')
FLW_SECRET_HASH = os.getenv('FLW_SECRET_HASH')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT= os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# python manage.py tailwind start

# static/css/input.css gets recreated. its content is  
    # @tailwind base;
    # @tailwind components;
    # @tailwind utilities;
# NPM_BIN_PATH uncommented for windows

# debug is set to true
# running when debug is false: allowed_hosts should include localhost

# changed html, js files; collectstatic
# changed database; makemigrations