import asyncio
import logging
import time

from jsonschema import validate, ValidationError

from backend.app.agent.mcp_client import call_mcp_tool


logger = logging.getLogger(__name__)

# Only tools explicitly approved by our application
ALLOWED_TOOLS = {
    "search_github_issues"
}


async def dispatch_tool(
    tool_name: str,
    arguments: dict,
    available_tools: list[dict],
    timeout_seconds: int = 30
):
    """
    Validate and execute an MCP tool requested by the LLM.
    """

    start_time = time.perf_counter()

    try:

        # 1. Validate the requested tool name
        if tool_name not in ALLOWED_TOOLS:
            raise ValueError(f"Tool is not allowed: {tool_name}")

        # 2. Find the requested tool definition
        tool_definition = next(
            (
                tool for tool in available_tools
                if tool["name"] == tool_name
            ),
            None
        )

        if tool_definition is None:
            raise ValueError(f"Tool not found: {tool_name}")

        # 3. Validate argument format
        if not isinstance(arguments, dict):
            raise ValueError("Tool arguments must be a dictionary.")

        # 4. Validate arguments against MCP input schema
        input_schema = tool_definition["input_schema"]

        validate(
            instance=arguments,
            schema=input_schema
        )

        # 5. Execute the MCP tool with a timeout
        result = await asyncio.wait_for(
            call_mcp_tool(tool_name, arguments),
            timeout=timeout_seconds
        )

        # 6. Calculate execution duration
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2
        )

        logger.info(
            "Tool %s executed successfully in %s ms",
            tool_name,
            duration_ms
        )

        # 7. Return successful execution result
        return {
            "success": True,
            "tool_name": tool_name,
            "result": result,
            "duration_ms": duration_ms
        }

    except ValidationError as error:

        logger.warning(
            "Invalid arguments for tool %s: %s",
            tool_name,
            error.message
        )

        return {
            "success": False,
            "tool_name": tool_name,
            "error": f"Invalid tool arguments: {error.message}"
        }

    except asyncio.TimeoutError:

        logger.error("Tool execution timed out: %s", tool_name)

        return {
            "success": False,
            "tool_name": tool_name,
            "error": "Tool execution timed out."
        }

    except Exception as error:

        logger.exception("Tool execution failed: %s", tool_name)

        return {
            "success": False,
            "tool_name": tool_name,
            "error": str(error)
        }