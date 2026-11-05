from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.db.session import get_db
from backend.app.models.models import AgentRun, ExecutionEvent

router = APIRouter(prefix="/api/observability", tags=["Observability"])

@router.get("/metrics")
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """Fetch overview statistics for the dashboard."""
    total_runs = db.query(AgentRun).count()
    successful_runs = db.query(AgentRun).filter(AgentRun.status == "completed").count()
    failed_runs = db.query(AgentRun).filter(AgentRun.status == "failed").count()
    
    # Calculate average latency for completed runs
    avg_latency = db.query(func.avg(AgentRun.duration_ms)).filter(AgentRun.status == "completed").scalar()
    
    # Fetch recent runs
    runs = db.query(AgentRun).order_by(AgentRun.created_at.desc()).limit(10).all()

    return {
        "total_runs": total_runs,
        "successful_runs": successful_runs,
        "failed_runs": failed_runs,
        "avg_latency_ms": round(avg_latency or 0, 2),
        "recent_runs": [
            {
                "id": str(r.id),
                "trace_id": r.trace_id,
                "status": r.status,
                "duration_ms": r.duration_ms,
                "created_at": r.created_at.isoformat()
            }
            for r in runs
        ]
    }

@router.get("/runs/{run_id}")
def get_run_details(run_id: str, db: Session = Depends(get_db)):
    """Fetch specific run details and its chronological execution events."""
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    events = db.query(ExecutionEvent).filter(ExecutionEvent.run_id == run_id).order_by(ExecutionEvent.created_at.asc()).all()

    return {
        "id": str(run.id),
        "session_id": str(run.session_id),
        "trace_id": run.trace_id,
        "status": run.status,
        "duration_ms": run.duration_ms,
        "created_at": run.created_at.isoformat(),
        "events": [
            {
                "id": str(e.id),
                "event_type": e.event_type,
                "status": e.status,
                "duration_ms": e.duration_ms,
                "payload": e.payload,
                "created_at": e.created_at.isoformat()
            }
            for e in events
        ]
    }