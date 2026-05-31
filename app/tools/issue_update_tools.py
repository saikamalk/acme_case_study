from app.auth.tool_authorizer import authorize_tool
from app.auth.user_context import current_user
from app.db.queries import add_issue_update
from app.observability.logger import logger


def add_issue_update_tool(issue_id: int, update_text: str):
    user = current_user.get()
    authorize_tool("add_issue_update_tool", user)
    logger.info(f"Calling Tool: add_issue_update_tool with issue_id: {issue_id} and update_text: {update_text}")
    update_id = add_issue_update(issue_id, update_text)
    logger.info(f"Tool Completed: add_issue_update_tool. Result: {update_id}")
    return {"status": "created", update_id: update_id}