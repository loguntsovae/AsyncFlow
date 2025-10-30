from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.services import forward_request
from middleware.auth import auth_middleware

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
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication middleware
app.middleware("http")(auth_middleware)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def api_gateway(request: Request, path: str):
    """
    Main gateway route - forwards all requests to appropriate services.
    
    Path format: /{service}/{remaining_path}
    Example: /orders/123 -> forwards to Order Service
    """
    return await forward_request(request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}





if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )