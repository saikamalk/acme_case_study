import os

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from app.observability.resource import SERVICE_RESOURCE

provider = TracerProvider(resource=SERVICE_RESOURCE)
provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint=os.getenv("TRACE_PROVIDER_URL"), insecure=True))
)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("acme-agent")
