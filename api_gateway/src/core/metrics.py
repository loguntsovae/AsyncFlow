"""Gateway metrics collection and reporting."""
from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Request
import time

# Define metrics
REQUEST_COUNT = Counter(
    'gateway_requests_total',
    'Total count of requests by service and status',
    ['service', 'status']
)

REQUEST_LATENCY = Histogram(
    'gateway_request_latency_seconds',
    'Request latency by service',
    ['service']
)

UPSTREAM_ERRORS = Counter(
    'gateway_upstream_errors_total',
    'Total count of upstream service errors',
    ['service', 'error_type']
)

class MetricsMiddleware:
    async def __call__(self, request: Request, call_next):
        # Extract service from path
        path_parts = request.url.path.strip("/").split("/")
        service = path_parts[0] if path_parts else "unknown"
        
        start_time = time.time()
        try:
            response = await call_next(request)
            REQUEST_COUNT.labels(service=service, status=response.status_code).inc()
            return response
        except Exception as e:
            UPSTREAM_ERRORS.labels(
                service=service,
                error_type=type(e).__name__
            ).inc()
            raise
        finally:
            REQUEST_LATENCY.labels(service=service).observe(time.time() - start_time)

def get_metrics():
    """Get current metrics in Prometheus format."""
    return generate_latest()