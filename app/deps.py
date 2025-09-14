# app/deps.py  (PATCH)
from fastapi import Header, HTTPException, status
from .config import settings
import hmac

def verify_api_key(x_api_key: str | None = Header(None, alias="X-API-Key")) -> None:
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-API-Key")
    if not hmac.compare_digest(x_api_key, settings.reptile_api_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad API Key")
