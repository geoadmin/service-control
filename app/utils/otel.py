from os import getenv

from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.botocore import BotocoreInstrumentor
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.psycopg import PsycopgInstrumentor
from opentelemetry.instrumentation.system_metrics import SystemMetricsInstrumentor
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import set_tracer_provider


def strtobool(value: str) -> bool:
    """Convert a string representation of truth to true (1) or false (0).
    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    value = value.lower()
    if value in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    if value in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    raise ValueError(f"invalid truth value \'{value}\'")


def initialize_tracing() -> bool:
    tracing_enabled = not strtobool(getenv("OTEL_SDK_DISABLED", "false"))
    if tracing_enabled:
        if strtobool(getenv("OTEL_ENABLE_DJANGO", "false")):
            DjangoInstrumentor().instrument()
        if strtobool(getenv("OTEL_ENABLE_BOTO", "false")):
            BotocoreInstrumentor().instrument()
        if strtobool(getenv("OTEL_ENABLE_PSYCOPG", "false")):
            PsycopgInstrumentor().instrument()
        if strtobool(getenv("OTEL_ENABLE_LOGGING", "false")):
            LoggingInstrumentor().instrument()
        if strtobool(getenv("OTEL_ENABLE_METRICS", "false")):
            SystemMetricsInstrumentor().instrument()
    return tracing_enabled


def setup_trace_provider() -> None:
    tracing_enabled = not strtobool(getenv("OTEL_SDK_DISABLED", "false"))
    if tracing_enabled:
        # Since we created a new tracer, the default span processor is gone. We need to
        # create a new one using the default OTEL env variables and ad it to the tracer.
        span_processor = BatchSpanProcessor(
            OTLPSpanExporter(
                endpoint=getenv('OTEL_EXPORTER_OTLP_ENDPOINT', "http://localhost:4317"),
                headers=getenv('OTEL_EXPORTER_OTLP_HEADERS'),
                insecure=strtobool(getenv('OTEL_EXPORTER_OTLP_INSECURE', "false"))
            )
        )
        trace_provider = TracerProvider(resource=Resource.create())
        trace_provider.add_span_processor(span_processor)
        set_tracer_provider(trace_provider)

        if strtobool(getenv("OTEL_ENABLE_METRICS", "false")):
            metric_reader = PeriodicExportingMetricReader(
                OTLPMetricExporter(
                    insecure=strtobool(getenv('OTEL_EXPORTER_OTLP_INSECURE', "false"))
                )
            )
            provider = MeterProvider([metric_reader])
            set_meter_provider(provider)
