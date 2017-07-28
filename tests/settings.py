"""
Test settings for rubber.
"""
import os

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

DEBUG = True

DATABASES = {
    'default': {
        'NAME': 'rubber.db',
        'ENGINE': 'django.db.backends.sqlite3',
        'TEST': {
            'NAME': 'rubber.db',
        },
        'TEST_NAME': 'rubber.db',
    }
}

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'rubber',
    'tests',
)

LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'rubber.tasks': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}

SECRET_KEY = 'secret-key'

##################################################
#                     Rubber                     #
##################################################

RUBBER = {
    'MODELS': [
        'tests.models.Token',
    ],
    'CONFIG_ROOT': os.path.join(SITE_ROOT, 'es_configs'),
    'OPTIONS': {
        'disabled': False,
        'fail_silently': True,
    },
}

##################################################
#                     Celery                     #
##################################################

CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

from . import celery_app  # noqa
