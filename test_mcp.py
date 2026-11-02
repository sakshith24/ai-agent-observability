import asyncio
from backend.app.agent.mcp_client import call_mcp_tool

async def main():
    print("Testing MCP client and tool...")
    result = await call_mcp_tool("search_github_issues", {"query": "WebSocket"})
    print("Result received:")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())