# What should this file do?

# 1. Accept conversation messages.
# 2. Accept available tool definitions.
# 3. Send everything to the LLM.
# 4. Receive the response.
# 5. Return the response to the orchestrator.

import os
import json
import logging
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# 1. Initialize OpenAI client
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not configured.")

    return AsyncOpenAI(api_key=api_key)


# 2. Convert MCP tools into OpenAI function tools
def convert_mcp_tools_to_openai(mcp_tools):

    openai_tools = []

    for tool in mcp_tools:

        name = tool["name"]
        description = tool["description"]
        input_schema = tool["input_schema"]

        openai_tool = {
            "type": "function",
            "name": name,
            "description": description,
            "parameters": input_schema,
            "strict": False
        }

        openai_tools.append(openai_tool)

    return openai_tools

# 3. Send request to OpenAI and interpret the response
async def get_llm_response(messages, tools):
    client = get_openai_client()
    response = await client.responses.create(
    model="gpt-4o-mini",
    input=messages,
    tools=tools
)
    tool_calls = []

    for item in response.output:

        # Step 4: Check whether the model requested a tool
        if item.type == "function_call":

            tool_calls.append({
                "call_id": item.call_id,
                "function_name": item.name,
                "arguments": json.loads(item.arguments)
            })

    # Step 5: If the model requested one or more tools
    if tool_calls:
        return {
            "type": "tool_call",
            "tool_calls": tool_calls,
            "output_items": response.output
        }

    # Step 6: Otherwise, return the final answer
    return {
        "type": "final_answer",
        "content": response.output_text,
        "output_items": response.output
    }


        