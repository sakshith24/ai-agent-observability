
import uuid
from fastapi import APIRouter, Depends, HTTPException
import time
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.models import (
    AgentRun,
    Session as ChatSession,
    Message,
)
from backend.app.agent.orchestrator import run_agent_orchestrator

router = APIRouter()


class ChatRequest(BaseModel):
    session_id: str
    message: str


@router.post("/chat")
async def start_chat(
    payload: ChatRequest,
    db: Session = Depends(get_db)
):
    # 1. Validate session ID
    try:
        session_uuid = uuid.UUID(payload.session_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid session ID format."
        )

    # 2. Check whether the chat session exists
    chat_session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_uuid)
        .first()
    )

    if not chat_session:
        raise HTTPException(
            status_code=404,
            detail="Session not found."
        )

    # 3. Save user message
    user_msg = Message(
        session_id=chat_session.id,
        role="user",
        content=payload.message
    )

    db.add(user_msg)
    db.commit()

    # 4. Create agent run
    run = AgentRun(
        session_id=chat_session.id,
        status="running"
    )

    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        # 5. Invoke the LLM-based orchestrator
        start_time = time.perf_counter()
        response_text = await run_agent_orchestrator(
            session_id=chat_session.id,
            db_session=db,
            run_id=run.id
        )

        # 6. Save assistant response
        assistant_msg = Message(
            session_id=chat_session.id,
            role="assistant",
            content=response_text
        )

        db.add(assistant_msg)

        # in millisec
        run.duration_ms = int((time.perf_counter() - start_time) * 1000)

        # 7. Mark agent run as completed
        run.status = "completed"
        db.commit()

        return {
            "session_id": str(chat_session.id),
            "run_id": str(run.id),
            "response": response_text,
            "duration_ms": run.duration_ms
        }

    except Exception:
        # Mark the run as failed if agent execution fails
        db.rollback()

        run = db.query(AgentRun).filter(
            AgentRun.id == run.id
        ).first()

        if run:
            run.status = "failed"
            db.commit()

        raise HTTPException(
            status_code=500,
            detail="Agent execution failed."
        )
