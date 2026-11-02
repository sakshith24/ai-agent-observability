import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.models import AgentRun, ExecutionEvent, Session as ChatSession, Message
from backend.app.agent.mcp_client import call_mcp_tool

router = APIRouter()

class ChatRequest(BaseModel):
    session_id: str
    message: str

@router.post("/chat")
async def start_chat(payload: ChatRequest, db: Session = Depends(get_db)):
    # 1. Validate session
    try:
        session_uuid = uuid.UUID(payload.session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format.")

    db_session = db.query(ChatSession).filter(ChatSession.id == session_uuid).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found.")

    # 2. Save user message
    user_msg = Message(session_id=db_session.id, role="user", content=payload.message)
    db.add(user_msg)
    db.commit()

    # 3. Create Agent Run
    run = AgentRun(session_id=db_session.id, status="running")
    db.add(run)
    db.commit()
    db.refresh(run)

    # 4. Invoke Real MCP Tool via Client
    tool_name = "search_github_issues"
    tool_results = await call_mcp_tool(tool_name, {"query": payload.message})

    # 5. Record execution event telemetry in PostgreSQL
    event = ExecutionEvent(
        run_id=run.id,
        event_type="mcp_tool_call",
        payload={"tool": tool_name, "query": payload.message, "result": tool_results}
    )
    db.add(event)
    
    run.status = "completed"
    db.commit()

    # 6. Format response for user and assistant message log
    response_text = f"MCP Tool Results for '{payload.message}':\n```json\n{tool_results}\n```"

    assistant_msg = Message(session_id=db_session.id, role="assistant", content=response_text)
    db.add(assistant_msg)
    db.commit()

    return {
        "session_id": str(db_session.id),
        "run_id": str(run.id),
        "response": response_text
    }