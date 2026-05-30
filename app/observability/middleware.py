import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from app.observability.logger import logger
from app.observability.trace_store import add_trace


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        trace_id = str(uuid.uuid4())
        start_time = time.time()

        logger.info(f"TRACE_ID={trace_id} | START REQUEST={request.url.path}")
        response = await call_next(request)
        latency = round((time.time() - start_time) * 1000, 2)
        logger.info(f"TRACE_ID={trace_id} |  END REQUEST={request.url.path} | LATENCY_MS={latency}")
        response.headers["X-Trace-Id"] = trace_id
        add_trace(
            {
                "trace_id": trace_id,
                "path": request.url.path,
                "method": request.method,
                "latency": latency,
            }
        )
        return response
