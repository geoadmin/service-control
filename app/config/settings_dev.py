import environ

from .settings_base import *  # noqa: F403

env = environ.Env()

# Override debug if given by the env
if env.bool('DEBUG', None):
    DEBUG = env.bool('DEBUG')

if DEBUG:
    INSTALLED_APPS += ['django_extensions', 'debug_toolbar']  # noqa: F405

if DEBUG:
    MIDDLEWARE = [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ] + MIDDLEWARE  # noqa: F405
