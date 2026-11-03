import asyncio
import json
from dotenv import load_dotenv

load_dotenv()

from backend.app.agent.llm_client import (
    get_llm_response,
    convert_mcp_tools_to_openai
)

from backend.app.agent.mcp_client import get_mcp_tools


async def main():

    # Step 1: Discover MCP tools
    mcp_tools = await get_mcp_tools()

    print("\nDiscovered MCP tools:")
    for tool in mcp_tools:
        print(tool["name"])

    # Step 2: Convert MCP tools into OpenAI format
    openai_tools = convert_mcp_tools_to_openai(mcp_tools)

    print("\nConverted OpenAI tools:")
    print(json.dumps(openai_tools, indent=2))

    # Step 3: Test normal conversation
    print("\n========== TEST 1: NORMAL RESPONSE ==========")

    messages = [
        {
            "role": "system",
            "content": "You are a helpful AI developer assistant."
        },
        {
            "role": "user",
            "content": "Hello! What can you help me with?"
        }
    ]

    result = await get_llm_response(messages, openai_tools)

    print("\nLLM Response:")
    print(json.dumps(result, indent=2, default=str))

    # Step 4: Test MCP tool selection
    print("\n========== TEST 2: TOOL CALL ==========")

    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI developer assistant. "
                "Use the search_github_issues tool when the user asks "
                "to search GitHub issues."
            )
        },
        {
            "role": "user",
            "content": "Find open GitHub issues related to WebSockets."
        }
    ]

    result = await get_llm_response(messages, openai_tools)

    print("\nLLM Response:")
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())