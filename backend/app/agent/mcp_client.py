import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def call_mcp_tool(tool_name: str, arguments: dict) -> list | dict:
    """Spawns the MCP server subprocess, connects via stdio, and calls a tool."""
    # Configure server parameters (points to your mcp_server/server.py script)
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server/server.py"],
        env=None
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 1. Initialize the connection
                await session.initialize()

                # 2. Invoke the requested tool with arguments
                result = await session.call_tool(tool_name, arguments=arguments)
                
                # 3. Parse content blocks returned by the tool
                for content in result.content:
                    if content.type == "text":
                        try:
                            return json.loads(content.text)
                        except json.JSONDecodeError:
                            return {"raw_text": content.text}
                            
                return {"error": "No valid text content returned from MCP server."}
                
    except Exception as e:
        print(f"MCP Client Connection Error: {e}")
        return {"error": f"Failed to connect to MCP server: {str(e)}"}