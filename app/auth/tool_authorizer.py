from fastapi import HTTPException
from app.auth.tool_permissions import TOOL_PERMISSIONS
from app.observability.logger import logger


def authorize_tool(tool_name: str, user):
    user_roles = user['roles']
    logger.info(f"Authorizing {tool_name} access for user: {user['username']}")
    allowed_roles = TOOL_PERMISSIONS.get(tool_name, [])
    if any(role in user_roles for role in allowed_roles):
        logger.info(f"{user['username']} authorized to access customer profile")
        return
    raise HTTPException(status_code=403, detail=f"User not authorized for tool: {tool_name}")
