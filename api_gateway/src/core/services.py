from typing import Optional, Any
import asyncio
import httpx
from fastapi import Request, HTTPException, status
from fastapi.responses import StreamingResponse

from core.config import settings


async def forward_request(request: Request) -> Any:
    """
    Forward request to appropriate service.
    
    This function:
    1. Extracts service name from path
    2. Forwards request to appropriate service
    3. Streams response back to client
    4. Preserves headers and status codes
    """
    path = request.url.path
    # If gateway exposes versioned API under /api/{version}/..., strip that prefix
    api_prefix = f"/api/{settings.API_VERSION}/"
    if path.startswith(api_prefix):
        path = path[len(api_prefix):]
    else:
        # Also allow bare /api/... (no version) by stripping first two segments if present
        if path.startswith("/api/"):
            # remove leading /api/{something}/
            parts = path.strip("/").split("/")
            if len(parts) >= 2:
                path = "/" + "/".join(parts[2:]) if len(parts) > 2 else "/"

    path = path.strip("/")
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
    
    # Build headers to forward
    headers = dict(request.headers)
    headers.pop("host", None)
    if hasattr(request.state, "user"):
        headers["X-User"] = request.state.user.get("sub")

    # Prefer app-scoped http client created in lifespan; fall back to a local client
    client: Optional[httpx.AsyncClient] = getattr(request.app.state, "http_client", None)

    # Simple retry/backoff for transient errors
    max_attempts = 3
    backoff = 0.25
    last_exc = None

    for attempt in range(1, max_attempts + 1):
        created_local_client = False
        try:
            if client is None:
                client = httpx.AsyncClient(timeout=settings.DEFAULT_TIMEOUT)
                created_local_client = True

            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=await request.body(),
                params=request.query_params,
                follow_redirects=True,
                timeout=settings.DEFAULT_TIMEOUT,
            )

            return StreamingResponse(
                response.aiter_raw(),
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type")
            )

        except (httpx.RequestError, httpx.TimeoutException) as e:
            last_exc = e
            # transient error -> retry with backoff
            if attempt < max_attempts:
                await asyncio.sleep(backoff * attempt)
                continue
            # final attempt failed
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service unavailable: {str(e)}"
            )
        finally:
            if created_local_client and client is not None:
                await client.aclose()