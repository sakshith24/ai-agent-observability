from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.models import AgentRun, ExecutionEvent

router = APIRouter()

class ChatRequest(BaseModel):
    session_id: str
    message:str

@router.post("/chat")
def start_chat(payload: ChatRequest, db: Session = Depends(get_db)):
    # 1. Create Agent Run record
    run = AgentRun(session_id=payload.session_id, status="running")
    db.add(run)
    db.commit()
    db.refresh(run)

    # 2. Record execution event (e.g., MCP tool trigger simulation)
    event = ExecutionEvent(
        run_id=run.id,
        event_type="mcp_tool_call",
        payload={"tool": "search_github_issues", "query": payload.message}
    )
    db.add(event)
    
    # Update run status
    run.status = "completed"
    db.commit()

    return {
        "run_id": str(run.id),
        "response": f"Processed query '{payload.message}' using MCP tool successfully."
    }