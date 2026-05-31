from app.auth.tool_authorizer import authorize_tool

from app.auth.user_context import current_user
from app.db.queries import create_next_action
from app.observability.logger import logger


def create_next_action_tool(issue_id: int, action_text: str):
    user = current_user.get()
    authorize_tool("create_next_action_tool", user)
    logger.info(f"Calling Tool: create_next_action_tool with issue_id: {issue_id} and action_text: {action_text}")
    action_id = create_next_action(issue_id, action_text, user["username"])
    logger.info(f"Tool Completed: create_next_action_tool. Result: {action_id}")
    return {"status": "created", "action_id": action_id}
