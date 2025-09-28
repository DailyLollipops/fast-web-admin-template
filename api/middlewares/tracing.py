import time
import traceback

from fastapi import Request
from loguru import logger
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from starlette.middleware.base import BaseHTTPMiddleware


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
