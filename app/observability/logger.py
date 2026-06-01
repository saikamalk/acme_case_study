import logging
import os

from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler

from app.observability.resource import SERVICE_RESOURCE

os.makedirs("logs", exist_ok=True)

logger_provider = LoggerProvider(resource=SERVICE_RESOURCE)
set_logger_provider(logger_provider)

otel_handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler(),
        otel_handler,
    ],
)

logger = logging.getLogger("acme-agent")
