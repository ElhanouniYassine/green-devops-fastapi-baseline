from __future__ import annotations
import os
from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Super-simple bearer auth: token is read from env; default for dev/tests.
API_TOKEN = os.getenv("API_TOKEN", "devtoken")
security_scheme = HTTPBearer(auto_error=False)

async def require_auth(request: Request, creds: HTTPAuthorizationCredentials | None = None):
    # Try to parse credentials via HTTPBearer
    credentials = creds or await security_scheme(request)
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing credentials")
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth scheme")
    if credentials.credentials != API_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    # Return a trivial "user" for potential future use
    return {"sub": "tester", "scopes": ["items:read", "items:write"]}

def token_issuer() -> str:
    # For demo purposes, we "issue" the configured token so tests/clients can fetch it.
    return API_TOKEN
