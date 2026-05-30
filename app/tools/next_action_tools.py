from app.auth.tool_authorizer import authorize_tool

from app.auth.user_context import current_user
from app.db.queries import create_next_action


def create_next_action_tool(issue_id: int, action_text: str):
    user = current_user.get()
    authorize_tool("create_next_action_tool", user["roles"])
    action_id = create_next_action(issue_id, action_text, user["username"])
    return {
        "status": "created",
        "action_id": action_id
    }
