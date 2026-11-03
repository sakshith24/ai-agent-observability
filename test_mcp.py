import asyncio

from backend.app.agent.mcp_client import (
    get_mcp_tools,
    call_mcp_tool
)


async def main():

    # Test 1: Discover available tools
    tools = await get_mcp_tools()

    print("\nAvailable MCP tools:")

    for tool in tools:
        print(tool["name"])
        print(tool["description"])
        print(tool["input_schema"])

    # Test 2: Execute an MCP tool
    result = await call_mcp_tool(
        "search_github_issues",
        {
            "query": "WebSocket",
            "status": "open"
        }
    )

    print("\nMCP Tool Result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
