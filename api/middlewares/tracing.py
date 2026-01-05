import sys
import time
import traceback

from fastapi import FastAPI, Request
from loguru import logger
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Status, StatusCode
from starlette.middleware.base import BaseHTTPMiddleware

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


class TracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        span = trace.get_current_span()
        trace_id = '0'
        if span and span.get_span_context().is_valid:
            trace_id = format(span.get_span_context().trace_id, '032x')

        try:
            response = await call_next(request)
        except Exception as exc:
            if span:
                span.record_exception(exc)
                stack = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
                span.set_attribute('exception.stacktrace', stack)
                span.set_status(Status(StatusCode.ERROR, str(exc)))
            logger.exception(f'Unhandled exception during {request.method} {request.url} (trace_id={trace_id})')
            raise
        finally:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            request.state.trace_id = trace_id
            request.state.elapsed_ms = elapsed_ms

        response.headers['X-Trace-ID'] = trace_id
        response.headers['X-Elapsed-Time'] = f'{elapsed_ms:.2f}ms'
        return response
