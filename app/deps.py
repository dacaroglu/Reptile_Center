from fastapi import Header, HTTPException, status
from .config import settings
import hmac, secrets

def verify_api_key(x_api_key: str = Header(default=None, convert_underscores=False)) -> None:
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-API-Key")
    # Constant-time compare
    if not hmac.compare_digest(x_api_key, settings.reptile_api_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad API Key")
