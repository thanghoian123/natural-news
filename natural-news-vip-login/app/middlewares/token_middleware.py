import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from app.core.config import SECRET_KEY, ALGORITHM

# List of public (no-auth) routes (without query parameters)
PUBLIC_PATHS = {"/users/login", '/users/verify-login', "/docs", "/openapi.json"}

class TokenExpiryMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extract only the path (without query parameters)
        path = request.url.path

        # Skip authentication for public paths
        if path in PUBLIC_PATHS:
            return await call_next(request)

        token = request.headers.get("Authorization")
        print('--token', token)
        if not token:
            return JSONResponse({"error": "Token missing"}, status_code=401)

        try:
            token = token.replace("Bearer ", "")  # Remove 'Bearer ' prefix
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            exp = payload.get("exp")  # Extract expiration timestamp
            if exp and exp < time.time():
                return JSONResponse({"error": "Token expired"}, status_code=401)

            request.state.user = payload  # Store user payload in request state
        except JWTError:
            return JSONResponse({"error": "Invalid token"}, status_code=401)

        return await call_next(request)
