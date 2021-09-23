import django.template.loaders.filesystem
import sys
from distutils.util import strtobool
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',    # https://github.com/encode/django-rest-framework/issues/6250
    'django.contrib.sites',        # allauth social login and dependency of dj_rest_auth password reset and registration
    'allauth',                     # allauth social login and dependency of dj_rest_auth registration
    'allauth.account',             # allauth social login and dependency of dj_rest_auth registration
    'allauth.socialaccount',       # allauth social login and dependency of dj_rest_auth registration
    'dj_rest_auth',                # enables authentication rest-api and user changes including password-reset
    'dj_rest_auth.registration',   # enables registration rest-api
    'lab_orchestrator_lib_django_adapter',
    'user',  # app that contains user model
    'user_auth',  # app for profile, authentication and registration; uses dj_rest_auth and allauth
    'instructions',  # app for profile, authentication and registration; uses dj_rest_auth and allauth
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lab_orchestrator.urls'

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

WSGI_APPLICATION = 'lab_orchestrator.wsgi.application'


DATABASE_ENGINE = os.environ.get("DATABASE_ENGINE", "sqlite3")
if DATABASE_ENGINE == "sqlite3":
    print("Loading sqlite3 database.", file=sys.stderr)
    SQLITE_PATH = BASE_DIR / 'volumes' / 'sqlite3' / 'db.sqlite3'
    # create sqlite path and parents if not exists
    Path(SQLITE_PATH).parent.mkdir(parents=True, exist_ok=True)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': SQLITE_PATH
        }
    }
elif DATABASE_ENGINE == "postgres":
    print("Loading postgres database.", file=sys.stderr)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get("POSTGRES_DB"),
            'USER': os.environ.get("POSTGRES_USER"),
            'PASSWORD': os.environ.get("POSTGRES_PASSWORD"),
            'HOST': os.environ.get("POSTGRES_SERVICE_HOST", "localhost"),
            'PORT': int(os.environ.get("POSTGRES_SERVICE_PORT", 5432)),
        }
    }
else:
    raise Exception(f"Wrong DATABASE_ENGINE set: {DATABASE_ENGINE}")


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.OrderingFilter',
        'rest_framework.filters.SearchFilter'
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
}


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Mail
EMAIL_USE_TLS = bool(strtobool(os.environ.get('EMAIL_USE_TLS', 'True')))
EMAIL_HOST = os.environ.get('EMAIL_HOST', None)
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', None)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', None)
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', "Django App")

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

SECRET_KEY = os.environ.get('SECRET_KEY', "changeme")
DEBUG = bool(strtobool(os.environ.get('DEBUG', 'False')))
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', "localhost;127.0.0.1;testing").split(";")
USE_X_FORWARDED_HOST = bool(strtobool(os.environ.get('USE_X_FORWARDED_HOST', 'False')))
DEVELOPMENT = bool(strtobool(os.environ.get("DEVELOPMENT", "False")))
LAB_VNC_HOST = os.environ.get("LAB_VNC_HOST", "localhost")
LAB_VNC_PORT = os.environ.get("LAB_VNC_PORT", "30003")
LAB_VNC_PROTOCOL = os.environ.get("LAB_VNC_PROTOCOL", "http")
LAB_VNC_PATH = os.environ.get("LAB_VNC_PATH", "vnc_lite.html")
WS_PROXY_HOST = os.environ.get("WS_PROXY_HOST", "localhost")
WS_PROXY_PORT = os.environ.get("WS_PROXY_PORT", "30002")

# custom user model
AUTH_USER_MODEL = 'user.User'

# redirect after authentication
LOGIN_REDIRECT_URL = '/api/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/api/'

# authentication
SITE_ID = 1
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = os.environ.get('ACCOUNT_EMAIL_VERIFICATION', 'optional')
REST_AUTH_SERIALIZERS = {
    'LOGIN_SERIALIZER': 'user_auth.serializers.CustomLoginSerializer',
    'USER_DETAILS_SERIALIZER': 'user_auth.serializers.CustomUserDetailsSerializer',
}
REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'user_auth.serializers.CustomRegisterSerializer',
}

