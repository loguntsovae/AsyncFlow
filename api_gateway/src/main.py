import datetime
import uuid
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import httpx
import structlog

from core.config import settings
from core.services import forward_request
from middleware.metrics import MetricsMiddleware, get_metrics
from middleware.auth import auth_middleware
from middleware.rate_limit import rate_limit_middleware

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    # Create HTTP client pool
    app.state.http_client = httpx.AsyncClient(timeout=settings.DEFAULT_TIMEOUT)
    yield
    await app.state.http_client.aclose()

# Create FastAPI application
app = FastAPI(
    title="AsyncFlow API Gateway",
    description="""
    AsyncFlow API Gateway - Unified interface for microservices.
    
    Available Services:
    * 🔒 Auth Service (/auth/*)
    * 📦 Order Service (/orders/*)
    * 💳 Billing Service (/billing/*)
    """,
    version=settings.API_VERSION,
    docs_url=f"/api/{settings.API_VERSION}/docs",
    redoc_url=f"/api/{settings.API_VERSION}/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add metrics middleware if enabled
if settings.ENABLE_METRICS:
    app.add_middleware(MetricsMiddleware)

# Add rate limiting if enabled
if settings.RATE_LIMIT_ENABLED:
    app.middleware("http")(rate_limit_middleware)

# Add authentication middleware
app.middleware("http")(auth_middleware)


@app.get("/health", tags=["System"])
async def health_check():
    """Enhanced health check endpoint with service status."""
    health_info = {
        "status": "healthy",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "version": settings.API_VERSION,
        "services": {}
    }
    
    # Check each service
    for service_name, config in settings.SERVICE_ROUTES.items():
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f"{config['host']}/health")
                health_info["services"][service_name] = {
                    "status": "up" if response.status_code == 200 else "degraded",
                    "latency_ms": int(response.elapsed.total_seconds() * 1000)
                }
        except Exception as e:
            health_info["services"][service_name] = {
                "status": "down",
                "error": str(e)
            }
            if all(svc.get("status") == "down" for svc in health_info["services"].values()):
                health_info["status"] = "unhealthy"
            else:
                health_info["status"] = "degraded"
    
    return health_info

# Backward/forward-compatible alias: expose health under versioned path as well
@app.get(f"/api/{settings.API_VERSION}/health", tags=["System"])
async def health_check_versioned():
    return await health_check()

@app.get("/metrics", tags=["System"], include_in_schema=settings.ENABLE_METRICS)
async def metrics():
    """Prometheus metrics endpoint."""
    if not settings.ENABLE_METRICS:
        raise HTTPException(status_code=404)
    return Response(content=get_metrics(), media_type="text/plain")

@app.api_route("/api/{version}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def api_gateway(request: Request, version: str, path: str):
    """
    Main gateway route - forwards all requests to appropriate services.
    
    Path format: /api/{version}/{service}/{remaining_path}
    Example: /api/v1/orders/123 -> forwards to Order Service
    """
    if version != settings.API_VERSION:
        raise HTTPException(
            status_code=404,
            detail=f"API version {version} not found. Current version: {settings.API_VERSION}"
        )
    
    # Add request context for logging
    request_id = str(uuid.uuid4())
    logger.info(
        "incoming_request",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host if request.client else None,
    )
    
    try:
        response = await forward_request(request)
        logger.info(
            "request_completed",
            request_id=request_id,
            status_code=response.status_code
        )
        return response
    except Exception as e:
        logger.error(
            "request_failed",
            request_id=request_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise





if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )