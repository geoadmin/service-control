import os

from .settings_dev import *  # pylint: disable=wildcard-import, unused-wildcard-import

TESTING = True
SECRET_KEY = 'django-insecure-6-72r#zx=sv6v@-4k@uf1gv32me@%yr*oqa*fu8&5l&a!ws)5#'  # nosec B105

# The tests use the default database, remove the BOD so that django doesn't try to create it
del DATABASES['bod']

os.environ["NINJA_SKIP_REGISTRY"] = "yes"
