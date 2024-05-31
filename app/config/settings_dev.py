import environ

from .settings_base import *  # pylint: disable=wildcard-import, unused-wildcard-import

env = environ.Env()

DEBUG = env.bool('DEBUG', True)

if DEBUG:
    INSTALLED_APPS += ['django_extensions', 'debug_toolbar']

if DEBUG:
    MIDDLEWARE = [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ] + MIDDLEWARE
