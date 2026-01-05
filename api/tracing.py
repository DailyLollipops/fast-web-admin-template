import sys

from fastapi import FastAPI
from loguru import logger
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from api.settings import settings


def instrument_loguru():
    def add_trace_context(record):
        record['extra']['otelSpanID'] = '0'
        record['extra']['otelTraceID'] = '0'
        record['extra']['otelTraceSampled'] = False
        record['extra']['otelServiceName'] = settings.APP_NAME

        span = trace.get_current_span()
        if span != trace.INVALID_SPAN:
            ctx = span.get_span_context()
            if ctx != trace.INVALID_SPAN_CONTEXT:
                record['extra']['otelSpanID'] = format(ctx.span_id, '016x')
                record['extra']['otelTraceID'] = format(ctx.trace_id, '032x')
                record['extra']['otelTraceSampled'] = ctx.trace_flags.sampled

    logger.configure(patcher=add_trace_context)


def setup_logging():
    logger.remove()
    logger.add(
        sys.stdout,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
            "| <level>{level: <8}</level> "
            "| trace_id={extra[otelTraceID]} span_id={extra[otelSpanID]} "
            "| {name}:{function}:{line} - {message}"
        ),
        level="INFO",
    )

def setup_tracing(app: FastAPI):
    resource = Resource(attributes={
        SERVICE_NAME: settings.APP_NAME,
    })
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    exporter = OTLPSpanExporter()
    span_processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(span_processor)

    FastAPIInstrumentor.instrument_app(app)
    SQLAlchemyInstrumentor().instrument()
    setup_logging()
    instrument_loguru()
