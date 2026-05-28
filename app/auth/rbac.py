from fastapi import HTTPException


def require_role(user, allowed_roles):
    user_roles = user.get("realm_access", {}).get("roles", [])
    if not any(role in user_roles for role in allowed_roles):
        raise HTTPException(status_code=403, detail="Forbidden")
