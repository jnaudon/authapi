"""
Django settings for authapi project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

import djcelery
djcelery.setup_loader()

# Celery config
BROKER_URL = "amqp://guest:guest@localhost:5672//"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'zct2c=hlij$^0xu0i8o6c^phjc!=m)r(%h90th0yyx9r5dm))+'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # custom
    'api',
    'authmethods',
    'captcha',

    #3rd party
    'corsheaders',
    'djcelery',
    'django_nose',
)

PLUGINS = (
    # Add plugins here
)

if PLUGINS:
    INSTALLED_APPS += PLUGINS

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'wrap.LoggingMiddleware'
)

# change the test runner to the one provided by celery so that the tests that
# make use of celery work when ./manage.py test is executed
TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

ROOT_URLCONF = 'authapi.urls'

WSGI_APPLICATION = 'authapi.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# cors
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = (
        'localhost:9001',
)

ENABLE_CAPTCHA = True
PREGENERATION_CAPTCHA = 100

SMS_PROVIDER = "console"
SMS_DOMAIN_ID = ""
SMS_LOGIN = ""
SMS_PASSWORD = ""
SMS_URL = ""
SMS_SENDER_ID = ""
SMS_VOICE_LANG_CODE = ""

MAX_AUTH_MSG_SIZE = {
  "sms": 120,
  "email": 10000
}

SMS_BASE_TEMPLATE = "%s -- Agora Voting"

EMAIL_BASE_TEMPLATE = "%s\n\n -- Agora Voting https://agoravoting.com"

SMS_AUTH_CODE_URL = "https://agoravoting.example.com/#/election/%(authid)s/public/login"
EMAIL_AUTH_CODE_URL = "https://agoravoting.example.com/#/election/%(authid)s/public/login/%(email)s/%(code)s"

SIZE_CODE = 8
MAX_GLOBAL_STR = 512
MAX_EXTRA_FIELDS = 15
MAX_SIZE_NAME_EXTRA_FIELD = 1024

if PLUGINS:
    import importlib
    for plugin in PLUGINS:
        mod = importlib.import_module("%s.settings" % plugin)
        to_import = [name for name in dir(mod) if not name.startswith('_')]
        locals().update({name: getattr(mod, name) for name in to_import})

# Auth api settings
from auth_settings import *

try:
    from custom_settings import *
except:
    pass
