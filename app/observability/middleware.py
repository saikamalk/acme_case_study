import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from app.observability.logger import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        trace_id = str(uuid.uuid4())
        start_time = time.time()

        logger.info(
            f"TRACE_ID={trace_id} | "
            f"START REQUEST={request.url.path}"
        )
        response = await call_next(request)
        latency = round(
            (time.time() - start_time) * 1000,
            2
        )
        logger.info(
            f"TRACE_ID={trace_id} | "
            f"END REQUEST={request.url.path} | "
            f"LATENCY_MS={latency}"
        )
        response.headers["X-Trace-Id"] = trace_id
        return response
