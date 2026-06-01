import time

from opentelemetry import trace
from starlette.middleware.base import BaseHTTPMiddleware

from app.observability.logger import logger
from app.observability.trace_store import tracer


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        with tracer.start_as_current_span(
                f"{request.method} {request.url.path}",
                kind=trace.SpanKind.SERVER,
        ) as span:
            span.set_attribute("http.method", request.method)
            span.set_attribute("http.url", str(request.url))

            start_time = time.time()
            otel_traec_id = format(span.get_span_context().trace_id, "032x")

            logger.info(f"TRACE_ID={otel_traec_id} | START REQUEST={request.url.path}")
            try:
                response = await call_next(request)
                latency = round((time.time() - start_time) * 1000, 2)
                span.set_attribute("http.status_code", response.status_code)
                span.set_attribute("http.latency_ms", latency)

                logger.info(
                    f"TRACE_ID={otel_traec_id} |  END REQUEST={request.url.path} | "
                    f"STATUS={response.status_code} | LATENCY_MS={latency}"
                )
                response.headers["X-Trace-Id"] = otel_traec_id
                return response
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.StatusCode.ERROR, str(e))
                logger.error(f"TRACE_ID={otel_traec_id} | ERROR={e}", exc_info=True)
                raise
