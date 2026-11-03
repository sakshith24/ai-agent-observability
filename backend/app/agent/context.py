from sqlalchemy.orm import Session
from backend.app.models.models import Message


SYSTEM_PROMPT = (
    "You are an AI assistant integrated into an Agent Observability platform. "
    "You have access to MCP tools to search GitHub issues. "
    "Always be precise, structured, and helpful. "
    "Use tools when they are relevant to the user's request. "
    "Never claim that you executed a tool unless it actually ran."
)


def build_agent_context(
    session_id: str,
    db_session: Session,
    limit: int = 10
) -> list[dict]:

    """
    Retrieves the latest chat messages from PostgreSQL
    and formats them into an LLM-ready message array.
    """

    if limit < 1:
        raise ValueError("Message limit must be at least 1.")

    # 1. Fetch the latest messages
    messages = (
        db_session.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
        .all()
    )

    # 2. Reverse to maintain chronological order
    messages.reverse()

    # 3. Add system instructions
    formatted_context = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    # 4. Convert database messages into LLM format
    for msg in messages:

        if msg.role not in ["user", "assistant"]:
            continue

        formatted_context.append({
            "role": msg.role,
            "content": msg.content
        })

    return formatted_context
