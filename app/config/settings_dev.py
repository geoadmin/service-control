import environ

from .settings_base import *  # pylint: disable=wildcard-import, unused-wildcard-import

env = environ.Env()

# Override debug if given by the env
if env.bool('DEBUG', None):
    DEBUG = env.bool('DEBUG')

if DEBUG:
    INSTALLED_APPS += ['django_extensions', 'debug_toolbar']

if DEBUG:
    MIDDLEWARE = [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ] + MIDDLEWARE
