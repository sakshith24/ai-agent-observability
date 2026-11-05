from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.models import AgentRun, ExecutionEvent
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()

# @router.get("/runs")
# def list_runs(db: Session = Depends(get_db)):
#     runs = db.query(AgentRun).all()
#     return [{"id": str(r.id), "session_id": str(r.session_id), "status": r.status} for r in runs]

@router.get("/runs/{run_id}")
def get_run_details(run_id: str, db: Session = Depends(get_db)):
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    # Query associated execution events for this run
    events = db.query(ExecutionEvent).filter(ExecutionEvent.run_id == run_id).all()

    # Return a dictionary containing all fields expected by the frontend
    return {
        "id": str(run.id),
        "session_id": str(run.session_id) if run.session_id else None,
        "trace_id": run.trace_id,
        "status": run.status,
        "duration_ms": run.duration_ms,
        "created_at": run.created_at.isoformat() if run.created_at else None,
        "events": [
            {
                "id": str(event.id),
                "event_type": event.event_type,
                "status": event.status,
                "duration_ms": event.duration_ms,
                "payload": event.payload,
                "created_at": event.created_at.isoformat() if event.created_at else None,
            }
            for event in events
        ]
    }
