from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class ReplicationMiddleware(BaseHTTPMiddleware):
    """Middleware to handle replicated requests and prevent infinite loops"""
    
    async def dispatch(self, request: Request, call_next):
        # Check if this is a replicated request
        replicated_from = request.headers.get("X-Replicated-From")
        
        if replicated_from:
            logger.info(f"Processing replicated request from server {replicated_from}")
            # Add flag to request state to prevent further event publishing
            request.state.is_replicated = True
            request.state.source_server = replicated_from
        else:
            request.state.is_replicated = False
            request.state.source_server = None
        
        response = await call_next(request)
        return response