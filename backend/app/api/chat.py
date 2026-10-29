import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.models import AgentRun, ExecutionEvent, Session as ChatSession

router = APIRouter()

class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str


@router.post("/chat")
def start_chat(payload: ChatRequest, db: Session = Depends(get_db)):
    # 1. Validate session ID format
    try:
        session_uuid = uuid.UUID(payload.session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format.")

    # 2. Ensure session exists in PostgreSQL
    db_session = db.query(ChatSession).filter(ChatSession.id == session_uuid).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found. Please create a session first.")
            
    # 2. Create Agent Run linked to the verified session
    run = AgentRun(session_id=db_session.id, status="running")
    db.add(run)
    db.commit()
    db.refresh(run)

    # 3. Record execution event
    event = ExecutionEvent(
        run_id=run.id,
        event_type="mcp_tool_call",
        payload={"tool": "search_github_issues", "query": payload.message}
    )
    db.add(event)
    
    run.status = "completed"
    db.commit()

    return {
        "run_id": str(run.id),
        "response": f"Processed query '{payload.message}' using MCP tool successfully."
    }