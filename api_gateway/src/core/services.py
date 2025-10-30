from typing import Optional, Dict, Any
import httpx
from fastapi import Request, HTTPException, status
from fastapi.responses import StreamingResponse

from core.config import settings

http_client = httpx.AsyncClient()


async def forward_request(request: Request) -> Any:
    """
    Forward request to appropriate service.
    
    This function:
    1. Extracts service name from path
    2. Forwards request to appropriate service
    3. Streams response back to client
    4. Preserves headers and status codes
    """
    path = request.url.path.strip("/")
    path_parts = path.split("/")
    
    if not path_parts:
        raise HTTPException(status_code=404, detail="Invalid path")
    
    service_name = path_parts[0]
    if service_name not in settings.SERVICE_ROUTES:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Get service configuration
    service_config = settings.SERVICE_ROUTES[service_name]
    service_host = service_config["host"]
    
    # Remove service prefix from path for forwarding
    forwarding_path = "/" + "/".join(path_parts[1:]) if len(path_parts) > 1 else "/"
    target_url = f"{service_host}{forwarding_path}"
    
    try:
        # Forward the request with all original properties
        headers = dict(request.headers)
        headers.pop("host", None)  # Remove host header
        
        # Add user info if available
        if hasattr(request.state, "user"):
            headers["X-User"] = request.state.user.get("sub")
        
        # Forward the request
        response = await http_client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=await request.body(),
            params=request.query_params,
            follow_redirects=True
        )
        
        # Stream the response back
        return StreamingResponse(
            response.aiter_raw(),
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type")
        )
        
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unavailable: {str(e)}"
        )