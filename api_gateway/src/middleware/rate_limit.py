"""Rate limiting middleware."""
from fastapi import Request, HTTPException
from datetime import datetime, timedelta
from typing import Dict, Tuple
import time

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, client_ip: str) -> bool:
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests.get(client_ip, [])
            if req_time > minute_ago
        ]
        
        # Check rate limit
        if len(self.requests.get(client_ip, [])) >= self.requests_per_minute:
            return False
        
        # Add new request
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        self.requests[client_ip].append(now)
        return True

rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    """Limit requests per client IP."""
    client_ip = request.client.host if request.client else "unknown"
    
    # Skip rate limiting for health check
    if request.url.path == "/health":
        return await call_next(request)
    
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Too many requests",
            headers={"Retry-After": "60"}
        )
    
    return await call_next(request)