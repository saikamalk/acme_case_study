import os
from typing import Any

from mcp.server.fastmcp import FastMCP

from mcp_server.db.queries import add_issue_update, create_next_action, get_issue_updates
from mcp_server.services.customer_service import CustomerService

mcp = FastMCP(
    "Acme Operations MCP",
    json_response=True,
    stateless_http=True,
    host=os.getenv("MCP_HOST"),
    port=int(os.getenv("MCP_PORT")),
)


@mcp.tool()
def customer_profile_tool(customer_name: str) -> dict[str, Any]:
    profile = CustomerService.fetch_customer_profile(customer_name)
    if not profile:
        return {
            "error": "Customer not found",
            "customer_name": customer_name,
        }
    return profile


@mcp.tool()
def issue_history_tool(issue_id: int) -> list[dict[str, Any]] | dict[str, Any]:
    updates = get_issue_updates(issue_id)
    if not updates:
        return {
            "error": "Issue not found or no history available",
            "issue_id": issue_id,
        }
    return updates


@mcp.tool()
def add_issue_update_tool(issue_id: int, update_text: str) -> dict[str, Any]:
    update_id = add_issue_update(issue_id, update_text)
    return {
        "status": "created",
        "update_id": update_id,
    }


@mcp.tool()
def create_next_action_tool(
        issue_id: int,
        action_text: str,
        created_by: str,
) -> dict[str, Any]:
    action_id = create_next_action(issue_id, action_text, created_by)
    return {
        "status": "created",
        "action_id": action_id,
    }


app = mcp.streamable_http_app()
