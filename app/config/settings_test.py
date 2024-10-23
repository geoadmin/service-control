from .settings_dev import *  # pylint: disable=wildcard-import, unused-wildcard-import

TESTING = True

# The tests use the default database, remove the BOD so that django doesn't try to create it
del DATABASES['bod']
