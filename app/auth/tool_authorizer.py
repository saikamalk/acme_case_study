from fastapi import HTTPException
from app.auth.tool_permissions import TOOL_PERMISSIONS, SKILLS_PERMISSIONS
from app.observability.logger import logger


def authorize_plan(plan, user):
    user_roles = user['roles']
    logger.info(f"Authorizing {plan.model_dump()} for user: {user['username']}")
    allowed_roles = TOOL_PERMISSIONS.get(plan.tool_name, [])
    auth_results = ""
    if any(role in user_roles for role in allowed_roles):
        logger.info(f"{user['username']} authorized to access {plan.tool_name}")
    else:
        auth_results += f"User not authorized to access the tool: {plan.tool_name}."
    allowed_roles = SKILLS_PERMISSIONS.get(plan.response_mode, [])
    if any(role in user_roles for role in allowed_roles):
        logger.info(f"{user['username']} authorized for {plan.response_mode} skill")
    else:
        auth_results += f"User not authorized for {plan.response_mode}."
    if auth_results == "":
        return
    raise HTTPException(status_code=403, detail=auth_results)
