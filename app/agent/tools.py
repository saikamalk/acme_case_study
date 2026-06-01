from app.mcp.client import execute_mcp_tool


async def customer_lookup(customer_name: str):
    return await execute_mcp_tool(
        "customer_profile_tool",
        {"customer_name": customer_name},
    )


async def issue_history_lookup(issue_id: str):
    return await execute_mcp_tool(
        "issue_history_tool",
        {"issue_id": int(issue_id)},
    )


async def add_issue_update_tool(issue_id: int, update_text: str):
    return await execute_mcp_tool(
        "add_issue_update_tool",
        {
            "issue_id": issue_id,
            "update_text": update_text,
        },
    )


async def create_next_action_tool(issue_id: int, action_text: str, user: dict):
    return await execute_mcp_tool(
        "create_next_action_tool",
        {
            "issue_id": issue_id,
            "action_text": action_text,
            "created_by": user["username"],
        },
    )
