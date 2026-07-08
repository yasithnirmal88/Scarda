from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware that checks for an Authorization header on protected routes."""

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith(("/api/auth", "/docs", "/openapi.json")):
            return await call_next(request)

        token = request.headers.get("Authorization")
        if not token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing authorization header"},
            )
        return await call_next(request)
