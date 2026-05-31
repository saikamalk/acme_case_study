from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose.exceptions import JWTError
from app.auth.keycloak import decode_token
from app.db.queries import get_user_role
from app.observability.logger import logger

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    logger.info(f"Authorizing user: {credentials.credentials}")
    token = credentials.credentials
    try:
        payload = decode_token(token)
        roles = payload.get("realm_access", {}).get("roles", [])
        username = payload.get("preferred_username") or payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Token missing username")

        app_role = get_user_role(username)
        if not app_role:
            raise HTTPException(status_code=403, detail=f"No app role configured for user: {username}")
        logger.info(f"User {username} configured for role {app_role}")
        return {
            "username": username,
            "roles": [app_role],
            "raw_payload": payload,
        }
    except JWTError as e:
        logger.error("JWT validation failed: %s", e, exc_info=True)
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Unexpected auth error: %s", e, exc_info=True)
        raise HTTPException(status_code=401, detail="Authentication failed")
