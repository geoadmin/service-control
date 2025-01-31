from .settings_base import *  # pylint: disable=wildcard-import, unused-wildcard-import

DEBUG = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_ROOT = BASE_DIR / 'var' / 'www' / 'service_control' / 'static_files'
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
