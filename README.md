# MCP-Powered AI Developer Assistant with Agent Observability Dashboard

An AI-powered developer assistant that uses the Model Context Protocol (MCP) to interact with developer tools, execute tasks, and provide context-aware responses.

The project aims to combine agentic AI workflows with real-time observability, allowing developers to understand, monitor, and debug how AI agents execute tasks through LLM calls, tool invocations, and API interactions.

## Overview

AI agents can perform complex tasks by interacting with external tools and APIs. However, understanding their execution flow, identifying failures, and monitoring performance can be challenging.

This project aims to address that challenge by building a full-stack AI developer assistant with an integrated observability dashboard.

Users will be able to interact with an AI assistant, while developers can inspect agent execution history, tool calls, errors, and performance metrics through a centralized dashboard.

## Key Features

### AI Developer Assistant
- Conversational interface for interacting with an AI assistant.
- Context-aware responses using LLM integration.
- Ability to perform developer-oriented tasks using external tools.

### MCP Integration
- Implement an MCP server to expose developer tools.
- Discover and invoke tools through the Model Context Protocol.
- Support MCP tools, resources, and prompts.
- Integrate with GitHub APIs for repository and issue-related operations.

### Agent Observability
- Track individual agent execution runs.
- Record LLM calls and MCP tool invocations.
- Store execution events and associated metadata.
- Inspect execution status, errors, and latency.
- Maintain historical agent execution records.

### Real-Time Monitoring
- Stream agent responses progressively.
- Display tool execution events as they happen.
- Handle connection interruptions and reconnection.
- Provide loading, error, and fallback states.

### Analytics Dashboard
- View previous agent executions.
- Monitor successful and failed runs.
- Analyze execution latency.
- Inspect individual execution traces and tool activity.

## System Architecture

The application follows a modular monorepo architecture consisting of four main components:

1. **Frontend:** Next.js and TypeScript for the conversational interface and observability dashboard.
2. **Backend:** FastAPI for API management, agent orchestration, and communication between system components.
3. **MCP Server:** Exposes developer tools, resources, and prompts using the Model Context Protocol.
4. **Database:** PostgreSQL for persistent storage of sessions, conversations, agent runs, and execution events.

### Architecture Flow

```text
                 User
                  |
                  v
        Next.js + TypeScript
          (Frontend UI)
                  |
             REST / SSE
             WebSockets
                  |
                  v
             FastAPI
                  |
          Agent Orchestrator
                  |
          +-------+-------+
          |               |
          v               v
       LLM Client      MCP Client
          |               |
          v               v
       LLM API         MCP Server
                          |
                          v
                    Developer Tools
                     (GitHub APIs)
                          |
                          v
                    Tool Results
                          |
                          v
                   Agent Response
                          |
                          v
                    Frontend UI

              PostgreSQL Database
                       |
             Execution History
             Agent Runs & Events
                       |
                       v
              Observability Dashboard
```

## Technology Stack

| Category | Technologies |
|---|---|
| Frontend | Next.js, React.js, TypeScript |
| Backend | Python, FastAPI |
| Agent Framework | Custom agent orchestration |
| AI Integration | LLM API |
| Agent Communication | Model Context Protocol (MCP) |
| Real-Time Communication | WebSockets, Server-Sent Events (SSE) |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Database Migrations | Alembic |
| Testing | Pytest, frontend testing tools |
| Development Tools | Git, GitHub, VS Code |

## Project Structure

```text
ai-agent-observability/
│
├── frontend/
│   └── src/
│       ├── app/
│       ├── components/
│       ├── lib/
│       └── types/
│
├── backend/
│   └── app/
│       ├── api/
│       ├── agent/
│       ├── core/
│       ├── db/
│       ├── models/
│       ├── schemas/
│       ├── services/
│       └── observability/
│
├── mcp_server/
│   ├── server.py
│   ├── tools/
│   ├── resources/
│   └── prompts/
│
├── infra/
│
├── .env.example
├── .gitignore
└── README.md
```

## Database Design

PostgreSQL is used to maintain persistent application and agent execution data.

Initial database entities:

| Table | Description |
|---|---|
| sessions | Stores conversation sessions |
| messages | Stores user and assistant messages |
| agent_runs | Tracks individual agent executions |
| execution_events | Records LLM calls, MCP tool calls, and errors |

Execution event payloads can store structured metadata in JSON/JSONB format.

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js and npm
- PostgreSQL
- Git

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-agent-observability.git

cd ai-agent-observability
```

### 2. Configure the backend

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Install backend dependencies using your project's package manager.

Configure your environment variables:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/ai_observability
OPENAI_API_KEY=your_api_key
```

### 3. Start the FastAPI backend

```bash
uvicorn backend.app.main:app --reload --port 8000
```

API documentation:

http://localhost:8000/docs

### 4. Start the MCP server

Run the MCP server using its configured transport and connection setup.

```bash
python mcp_server/server.py
```

### 5. Start the frontend

```bash
cd frontend

npm install

npm run dev
```

Open:

http://localhost:3000

*Note: The commands and environment configuration should be adjusted to match the final implementation and dependency setup.*


## Project Goals

The primary goal is to explore how agentic AI systems can be built, integrated, and monitored in a full-stack application.

The project focuses on:

- Building reliable AI-powered developer tools.
- Understanding MCP-based tool integration.
- Designing scalable backend APIs.
- Implementing real-time frontend/backend communication.
- Improving visibility into agent execution and failures.
- Developing practical experience with production-oriented AI application architecture.

## License

This project is currently under development. License and contribution guidelines will be added as the project evolves.
