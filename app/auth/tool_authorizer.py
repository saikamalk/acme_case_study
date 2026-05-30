from fastapi import HTTPException
from app.auth.tool_permissions import TOOL_PERMISSIONS


def authorize_tool(tool_name: str, user_roles: list):
    allowed_roles = TOOL_PERMISSIONS.get(tool_name, [])
    if any(role in user_roles for role in allowed_roles):
        return
    raise HTTPException(status_code=403, detail=f"User not authorized for tool: {tool_name}")
