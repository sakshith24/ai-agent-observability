
import sys
import json
import logging

from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


logger = logging.getLogger(__name__)


# --------------------------------------------------
# 1. Configure MCP server
# --------------------------------------------------

def get_server_parameters():

    # Get the project root directory
    project_root = Path(__file__).resolve().parents[3]

    # Locate MCP server.py
    server_file = project_root / "mcp_server" / "server.py"

    # Check whether the server file exists
    if not server_file.exists():
        raise FileNotFoundError(
            f"MCP server not found at: {server_file}"
        )

    return StdioServerParameters(
        command=sys.executable,
        args=[str(server_file)],
        env=None
    )


# --------------------------------------------------
# 2. Discover available MCP tools
# --------------------------------------------------

async def get_mcp_tools():

    server_params = get_server_parameters()

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            # Initialize MCP connection
            await session.initialize()

            # Ask MCP server for available tools
            result = await session.list_tools()

            tools = []

            for tool in result.tools:

                tools.append({
                    "name": tool.name,
                    "description": tool.description or "",
                    "input_schema": tool.inputSchema
                })

            logger.info("Discovered %d MCP tools", len(tools))

            return tools


# --------------------------------------------------
# 3. Execute an MCP tool
# --------------------------------------------------

async def call_mcp_tool(
    tool_name: str,
    arguments: dict
):

    server_params = get_server_parameters()

    try:

        async with stdio_client(server_params) as (read, write):

            async with ClientSession(read, write) as session:

                # Initialize MCP connection
                await session.initialize()

                # Execute requested MCP tool
                result = await session.call_tool(
                    tool_name,
                    arguments=arguments
                )

                # Check whether MCP returned an error
                if result.isError:
                    raise RuntimeError(
                        f"MCP tool execution failed: {tool_name}"
                    )

                # Prefer structured output
                if result.structuredContent is not None:
                    return result.structuredContent

                # Otherwise, extract text output
                text_blocks = [
                    content.text
                    for content in result.content
                    if content.type == "text"
                ]

                if not text_blocks:
                    return {
                        "success": False,
                        "error": "MCP tool returned no usable content."
                    }

                combined_text = "\n".join(text_blocks)

                # Try converting JSON text into Python data
                try:
                    return json.loads(combined_text)

                except json.JSONDecodeError:
                    return {
                        "raw_text": combined_text
                    }

    except Exception:

        logger.exception(
            "Failed to execute MCP tool: %s",
            tool_name
        )

        raise

