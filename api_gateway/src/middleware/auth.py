from fastapi import Request, HTTPException, status
from core.config import settings
from core.security import verify_token


def is_public_path(path: str) -> bool:
    """Check if the path is public."""
    if path == "health":
        return True
        
    path_parts = path.strip("/").split("/")
    if len(path_parts) < 2:
        return False
        
    service = path_parts[0]
    if service not in settings.SERVICE_ROUTES:
        return False
        
    service_config = settings.SERVICE_ROUTES[service]
    remaining_path = "/" + "/".join(path_parts[1:])
    return remaining_path in service_config["public_paths"]


async def auth_middleware(request: Request, call_next):
    """Authenticate requests before routing."""
    path = request.url.path
    
    # Skip authentication for public paths
    if is_public_path(path):
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