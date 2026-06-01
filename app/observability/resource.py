from opentelemetry.sdk.resources import Resource

SERVICE_RESOURCE = Resource.create(
    {
        "service.name": "acme-agent",
        "service.version": "1.0.0",
        "deployment.environment": "local"
    }
)
