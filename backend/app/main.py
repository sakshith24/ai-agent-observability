from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api import chat, runs, health
from backend.app.db.session import engine, Base

Base.metadata.create_all(bind=engine)

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