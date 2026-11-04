import json
import logging
import time
from backend.app.agent.context import build_agent_context
from backend.app.agent.mcp_client import get_mcp_tools
from backend.app.agent.llm_client import (get_llm_response,convert_mcp_tools_to_openai)
from backend.app.agent.tool_dispatcher import dispatch_tool
from backend.app.models.models import ExecutionEvent , AgentRun


logger = logging.getLogger(__name__)

def log_event(
    db_session,
    run_id,
    trace_id,
    event_type,
    status,
    payload=None,
    duration_ms=None
):
    """Save an execution event to PostgreSQL."""

    event = ExecutionEvent(
        run_id=run_id,
        trace_id=trace_id,
        event_type=event_type,
        status=status,
        payload=payload or {},
        duration_ms=duration_ms
    )

    db_session.add(event)
    db_session.commit()
    
async def run_agent_orchestrator(
    session_id,
    db_session,
    run_id,
    max_iterations=5
):
    """
    Coordinates the LLM, MCP tools, and tool dispatcher
    to complete an agent request.
    """

    # 1. Build conversation context
    messages = build_agent_context(
        session_id,
        db_session
    )

    # 2. Discover available MCP tools
    mcp_tools = await get_mcp_tools()

    # 3. Convert MCP tools into OpenAI format
    openai_tools = convert_mcp_tools_to_openai(mcp_tools)

    logger.info("Agent started for run_id: %s", run_id)

    # 4. Start the agent execution loop
    for iteration in range(max_iterations):

        logger.info(
            "Agent iteration: %s",
            iteration + 1
        )

        # 5. Ask OpenAI what to do next
        llm_result = await get_llm_response(
            messages,
            openai_tools
        )

        # 6. Check whether OpenAI returned a final answer
        if llm_result["type"] == "final_answer":

            logger.info("Agent generated final answer.")

            return llm_result["content"]

        # 7. Check whether OpenAI requested a tool
        if llm_result["type"] == "tool_call":

            # Preserve original OpenAI output items
            messages.extend(
                llm_result["output_items"]
            )

            # 8. Execute each requested tool
            for tool_call in llm_result["tool_calls"]:

                tool_name = tool_call["function_name"]
                arguments = tool_call["arguments"]
                call_id = tool_call["call_id"]

                # Dispatch and execute the tool
                tool_result = await dispatch_tool(
                    tool_name=tool_name,
                    arguments=arguments,
                    available_tools=mcp_tools
                )

                # 9. Record tool execution in PostgreSQL
                event = ExecutionEvent(
                    run_id=run_id,
                    event_type="mcp_tool_call",
                    payload={
                        "tool": tool_name,
                        "success": tool_result["success"],
                        "duration_ms": tool_result.get("duration_ms"),
                        "error": tool_result.get("error")
                    }
                )

                db_session.add(event)
                db_session.commit()

                # 10. Send the tool result back to OpenAI
                messages.append({
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(
                        tool_result,
                        default=str
                    )
                })

    # 11. Stop if the iteration limit is reached
    logger.warning(
        "Agent reached maximum iterations: %s",
        max_iterations
    )

    return (
        "I couldn't complete the request within the "
        "maximum number of agent iterations."
    )