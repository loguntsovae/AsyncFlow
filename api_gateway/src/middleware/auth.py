from fastapi import Request, HTTPException, status
from core.config import settings
from core.security import verify_token

def is_public_path(path: str, method: str) -> bool:
    """Check if the path is public or should bypass auth.

    Supports both bare and versioned API prefixes (e.g., /api/v1/...).
    Also allows health and docs endpoints, and CORS preflight.
    """
    # Allow CORS preflight
    if method.upper() == "OPTIONS":
        return True

    normalized = path.strip("/")

    # Health endpoints
    if normalized == "health" or normalized == f"api/{settings.API_VERSION}/health":
        return True

    # Docs and OpenAPI
    docs_candidates = {
        "docs",
        "redoc",
        "openapi.json",
        f"api/{settings.API_VERSION}/docs",
        f"api/{settings.API_VERSION}/redoc",
        f"api/{settings.API_VERSION}/openapi.json",
    }
    if normalized in docs_candidates:
        return True

    # Determine service and remaining path with optional versioned prefix
    parts = normalized.split("/") if normalized else []
    if not parts:
        return False

    # Handle /api/{version}/{service}/...
    idx = 0
    if len(parts) >= 2 and parts[0] == "api" and parts[1] == settings.API_VERSION:
        idx = 2

    if len(parts) <= idx:
        return False

    service = parts[idx]
    if service not in settings.SERVICE_ROUTES:
        return False

    remaining_path = "/" + "/".join(parts[idx + 1:]) if len(parts) > idx + 1 else "/"
    service_config = settings.SERVICE_ROUTES[service]
    return remaining_path in service_config["public_paths"]


async def auth_middleware(request: Request, call_next):
    """Authenticate requests before routing."""
    path = request.url.path
    
    # Skip authentication for public paths
    if is_public_path(path, request.method):
        return await call_next(request)
    
    # Get token from header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify token
        payload = await verify_token(token)
        
        # Add user info to request state
        request.state.user = payload
        return await call_next(request)
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication format",
            headers={"WWW-Authenticate": "Bearer"},
        )