import os

import requests

from app.observability.logger import logger

MCP_BASE_URL = os.getenv("MCP_BASE_URL")


def execute_mcp_tool(tool_name: str, tool_input: str):
    response = requests.post(
        f"{MCP_BASE_URL}/execute/{tool_name}",
        json={
            "input": tool_input
        }
    )
    if not response.ok:
        raise Exception(f"MCP Error: {response.status_code} - {response.text}")
    return response.json()
