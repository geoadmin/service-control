import environ

from .settings_base import *  # pylint: disable=wildcard-import, unused-wildcard-import

env = environ.Env()

DEBUG = env.bool('DEBUG', True)

