import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.models import Session as ChatSession

router = APIRouter(prefix="/sessions", tags=["sessions"])

class SessionResponse(BaseModel):
    id: str
    title: str | None
    created_at: str | None

    class Config:
        from_attributes = True

@router.post("/", status_code=201)
def create_session(db: Session = Depends(get_db)):
    """Create a new chat session."""
    new_session = ChatSession(title="New Developer Chat")
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return {
        "session_id": str(new_session.id),
        "title": new_session.title,
        "created_at": str(new_session.created_at)
    }

@router.get("/")
def list_session(db: Session = Depends(get_db)):
    """List all chat sessions ordered by creation date."""
    sessions = db.query(ChatSession).order_by(ChatSession.created_at.desc()).all()
    return [
        {
            "session_id": str(s.id),
            "title": s.title,
            "created_at": str(s.created_at)
        }
        for s in sessions
    ] 