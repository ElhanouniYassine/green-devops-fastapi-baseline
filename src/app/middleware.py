from __future__ import annotations
import time, uuid, logging
from typing import Callable, Awaitable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import APIRouter
import structlog

# Prometheus metrics
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "path", "status"])
REQUEST_LATENCY = Histogram("http_request_latency_seconds", "Request latency", ["method", "path"])
INFLIGHT = Gauge("http_requests_in_flight", "In-flight HTTP requests")

metrics_router = APIRouter()

@metrics_router.get("/metrics")
def metrics_endpoint():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]):
        request_id = str(uuid.uuid4())
        start = time.perf_counter()
        INFLIGHT.inc()
        try:
            # attach request_id to context; make it accessible to structlog
            request.state.request_id = request_id
            structlog.contextvars.bind_contextvars(request_id=request_id, path=request.url.path, method=request.method)
            response = await call_next(request)
        finally:
            INFLIGHT.dec()
        elapsed = time.perf_counter() - start
        REQUEST_LATENCY.labels(request.method, request.url.path).observe(elapsed)
        REQUEST_COUNT.labels(request.method, request.url.path, str(response.status_code)).inc()
        # add header for tracing across services
        response.headers["X-Request-ID"] = request_id
        return response

def configure_logging():
    # minimal structlog config
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )

# OpenTelemetry tracing (console exporter for dev/CI)
def configure_tracing(service_name: str = "green-devops-fastapi"):
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter
        resource = Resource.create(attributes={"service.name": service_name})
        provider = TracerProvider(resource=resource)
        processor = SimpleSpanProcessor(ConsoleSpanExporter())
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
    except Exception:  # keep app running even if otel not available
        pass
