#!/usr/bin/env python
"""
WSGI config for project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

# isort:skip_file
# pylint: disable=wrong-import-position,wrong-import-order

# The gevent monkey import and patch suppress a warning, and a potential problem.
# Gunicorn would call it anyway, but if it tries to call it after the ssl module
# has been initialized in another module (like, in our code, by the botocore library),
# then it could lead to inconsistencies in how the ssl module is used. Thus we patch
# the ssl module through gevent.monkey.patch_all before any other import, especially
# the app import, which would cause the boto module to be loaded, which would in turn
# load the ssl module.
# NOTE: We do this only if wsgi.py is the main program, when running django runserver
# for local development, monkey patching creates the following error:
#     `RuntimeError: cannot release un-acquired lock`
if __name__ == '__main__':
    import gevent.monkey
    gevent.monkey.patch_all()

# default to the setting that's being created in DOCKERFILE
from os import environ

environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Initialize OTEL.
# Initialize should be called as early as possible, but at least before the app is imported
# The order has a impact on how the libraries are instrumented. If called after app import,
# e.g. the django instrumentation has no effect.
from utils.otel import initialize_tracing, setup_trace_provider

initialize_tracing()

from gunicorn.app.base import BaseApplication
from gunicorn.arbiter import Arbiter
from gunicorn.workers.base import Worker
from gunicorn.config import Config
from django.core.handlers.wsgi import WSGIHandler
from django.core.wsgi import get_wsgi_application

# Here we cannot use `from django.conf import settings` because it breaks the `make gunicornserve`
from config.settings_prod import get_logging_config

application = get_wsgi_application()


class StandaloneApplication(BaseApplication):  # pylint: disable=abstract-method

    cfg: Config

    def __init__(self, app: WSGIHandler, options: dict[str, object] | None = None) -> None:  # pylint: disable=redefined-outer-name
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self) -> None:
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self) -> WSGIHandler:  # type:ignore[override]
        return self.application


def post_fork(server: Arbiter, worker: Worker) -> None:
    if server.log:
        server.log.info("Worker spawned (pid: %s)", worker.pid)

    # Setup OTEL providers for this worker
    setup_trace_provider()


# We use the port 5000 as default, otherwise we set the HTTP_PORT env variable within the container.
if __name__ == '__main__':
    HTTP_PORT = str(environ.get('HTTP_PORT', "8000"))
    # Bind to 0.0.0.0 to let your app listen to all network interfaces.
    options = {
        'bind': f"{'0.0.0.0'}:{HTTP_PORT}",  # nosec B104
        'worker_class': 'gevent',
        'workers': int(environ.get('GUNICORN_WORKERS',
                                   '2')),  # scaling horizontally is left to Kubernetes
        'worker_tmp_dir': environ.get('GUNICORN_WORKER_TMP_DIR', None),
        'keepalive': int(environ.get('GUNICORN_KEEPALIVE', '2')),
        'timeout': 60,
        'logconfig_dict': get_logging_config(),
        'post_fork': post_fork,
    }
    StandaloneApplication(application, options).run()
