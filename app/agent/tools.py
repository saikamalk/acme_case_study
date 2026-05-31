import asyncio
from app.agent.entity_resolver import resolve_customer_name
from app.auth.tool_authorizer import authorize_tool
from app.auth.user_context import current_user
from app.mcp.client import execute_mcp_tool


async def customer_lookup(query: str):
    user = current_user.get()
    authorize_tool("customer_profile_tool", user)
    customer_name = await asyncio.to_thread(resolve_customer_name, query)
    if customer_name == "NONE":
        return {"error": "Customer not found"}
    return await execute_mcp_tool(
        "customer_profile_tool",
        {"customer_name": customer_name},
    )


async def issue_history_lookup(issue_id: str):
    user = current_user.get()
    authorize_tool("issue_history_tool", user)
    return await execute_mcp_tool(
        "issue_history_tool",
        {"issue_id": int(issue_id)},
    )


async def add_issue_update_tool(issue_id: int, update_text: str):
    user = current_user.get()
    authorize_tool("add_issue_update_tool", user)
    return await execute_mcp_tool(
        "add_issue_update_tool",
        {
            "issue_id": issue_id,
            "update_text": update_text,
        },
    )


async def create_next_action_tool(issue_id: int, action_text: str):
    user = current_user.get()
    authorize_tool("create_next_action_tool", user)
    return await execute_mcp_tool(
        "create_next_action_tool",
        {
            "issue_id": issue_id,
            "action_text": action_text,
            "created_by": user["username"],
        },
    )
