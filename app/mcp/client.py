import os
from typing import Any

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from app.observability.logger import logger

MCP_BASE_URL = os.getenv("MCP_BASE_URL").rstrip("/")
MCP_URL = f"{MCP_BASE_URL}/mcp"


async def execute_mcp_tool(tool_name: str, tool_arguments: dict[str, Any]) -> Any:
    async with streamable_http_client(MCP_URL) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools_response = await session.list_tools()
            available_tools = [tool.name for tool in tools_response.tools]
            if tool_name not in available_tools:
                raise ValueError(f"MCP tool not available: {tool_name}. Available tools: {available_tools}")
            logger.info(f"Calling MCP tool: {tool_name} args: {tool_arguments}")
            result = await session.call_tool(tool_name, arguments=tool_arguments)
            logger.info(f"MCP tool result: {result}")
            if getattr(result, "isError", False):
                raise RuntimeError(f"MCP tool failed: {result}")
            structured = getattr(result, "structuredContent", None)
            if structured is not None:
                return structured
            parts = []
            for content in getattr(result, "content", []):
                text = getattr(content, "text", None)
                if text:
                    parts.append(text)
            if parts:
                return "\n".join(parts)
            return result
