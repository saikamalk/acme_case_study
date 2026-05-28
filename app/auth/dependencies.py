from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer

from app.auth.keycloak import decode_token
from app.observability.logger import logger

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = decode_token(token)
        return {
            "username": payload.get("preferred_username"),
            "roles": payload.get("realm_access").get("roles", []),
            "raw_payload": payload,
        }
    except Exception as e:
        logger.error(e, exc_info=True)
        raise HTTPException(status_code=401)
