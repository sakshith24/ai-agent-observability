from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# 1. Load environment variables first
load_dotenv()

# 2. Import database engine, base, and the models module (this registers your tables)
from backend.app.db.session import engine, Base

# Import model classes so SQLAlchemy registers their tables.
from backend.app.models.models import (
    Session,
    Message,
    AgentRun,
    ExecutionEvent
)
print("Registered tables:", Base.metadata.tables.keys())
# Create missing tables.
Base.metadata.create_all(bind=engine)

from backend.app.api import chat, runs, health, session

app = FastAPI(title="AI Agent Observability Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(runs.router, prefix="/api", tags=["Runs"])
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(session.router, prefix="/api", tags=["session"])

@app.get("/health")
def health_check():
    return {"status": "healthy"}