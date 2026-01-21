#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from opentelemetry import trace
from utils.logging import redirect_std_to_logger
from utils.otel import initialize_tracing
from utils.otel import setup_trace_provider


def main() -> None:
    """Run administrative tasks."""
    # default to the setting that's being created in DOCKERFILE
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import \
            execute_from_command_line  # pylint: disable=import-outside-toplevel
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    tracing_enabled = initialize_tracing()
    if tracing_enabled:
        name = sys.argv[1] if len(sys.argv) > 1 else sys.argv[0]
        setup_trace_provider()
        tracer = trace.get_tracer(name)
        with tracer.start_as_current_span(name=name):
            execute_from_command_line(sys.argv)
    else:
        execute_from_command_line(sys.argv)


if __name__ == '__main__':
    if '--redirect-std-to-logger' in sys.argv:
        sys.argv.remove('--redirect-std-to-logger')
        with redirect_std_to_logger(__name__):
            main()
    else:
        main()
