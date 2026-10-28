from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.models import AgentRun

router = APIRouter()

@router.get("/runs")
def list_runs(db: Session = Depends(get_db)):
    runs = db.query(AgentRun).all()
    return [{"id": str(r.id), "session_id": str(r.session_id), "status": r.status} for r in runs]

@router.get("/runs/{run_id}")
def get_run(run_id: str, db: Session = Depends(get_db)):
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        return {"error": "Run not found"}
    return {"id": str(run.id), "status": run.status, "created_at": run.created_at}