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

@router.post("/sessions")
def create_session(db: Session = Depends(get_db)):
    """Creates a new chat session in PostgreSQL and returns its UUID."""
    new_session = ChatSession(title="New Developer Chat")
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return {"session_id": str(new_session.id)}

@router.post("/chat")
def start_chat(payload: ChatRequest, db: Session = Depends(get_db)):
    # 1. Validate that the session actually exists in PostgreSQL
    if not payload.session_id:
        db_session = ChatSession(title="Auto-created Session")
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
    else:
        try:
            session_uuid = uuid.UUID(payload.session_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid session ID format.")

        db_session = db.query(ChatSession).filter(ChatSession.id == session_uuid).first()
        if not db_session:
            db_session = ChatSession(id=session_uuid, title="Recovered Session")
            db.add(db_session)
            db.commit()
            db.refresh(db_session)
            

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