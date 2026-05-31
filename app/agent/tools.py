from langchain.tools import Tool

from app.agent.entity_resolver import resolve_customer_name
from app.auth.tool_authorizer import authorize_tool
from app.auth.user_context import current_user
from app.mcp.client import execute_mcp_tool
from app.observability.logger import logger


def customer_lookup(query: str):
    user = current_user.get()
    authorize_tool("customer_profile_tool", user)
    customer_name = resolve_customer_name(query)
    if customer_name == "NONE":
        return {"error": "Customer not found"}
    result = execute_mcp_tool("customer_profile_tool", customer_name)
    return str(result)


def issue_history_lookup(issue_id: str):
    user = current_user.get()
    authorize_tool("issue_history_tool", user)
    result = execute_mcp_tool("issue_history_tool", issue_id)
    return str(result)


customer_profile_tool = Tool(
    name="customer_profile_tool",
    func=customer_lookup,
    description="Retrieve customer profile and open issues using natural language references."
)

issue_history_tool = Tool(
    name="issue_history_tool",
    func=issue_history_lookup,
    description="Retrieve issue history using issue ID."
)
