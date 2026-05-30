from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose.exceptions import JWTError
from app.auth.keycloak import decode_token
from app.observability.logger import logger

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = decode_token(token)
        roles = payload.get("realm_access", {}).get("roles", [])
        username = payload.get("preferred_username") or payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Token missing username")
        return {
            "username": username,
            "roles": roles,
            "raw_payload": payload,
        }
    except JWTError as e:
        logger.error("JWT validation failed: %s", e, exc_info=True)
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected auth error: %s", e, exc_info=True)
        raise HTTPException(status_code=401, detail="Authentication failed")
