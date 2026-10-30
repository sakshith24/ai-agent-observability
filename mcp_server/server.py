from mcp.server.fastmcp import FastMCP
import json

mcp = FastMCP("Developer Assistant MCP")

# Mock dataset of GitHub issues
GITHUB_ISSUES = [
    {
        "id": 101,
        "title": "WebSocket client drops connection under heavy load",
        "tags": ["WebSocket", "reconnection", "network"],
        "status": "open",
        "description": "Clients lose connection when event loops spike above 50ms."
    },
    {
        "id": 102,
        "title": "PostgreSQL connection pool exhaustion",
        "tags": ["PostgreSQL", "database", "scaling"],
        "status": "closed",
        "description": "Async sessions were not being closed properly in FastAPI dependencies."
    },
    {
        "id": 103,
        "title": "Automatic reconnection retry logic failing",
        "tags": ["reconnection", "frontend", "websocket"],
        "status": "open",
        "description": "Exponential backoff timer resets prematurely on network drops."
    }
]

@mcp.tool()
def search_github_issues(query: str) -> str:
    """Search mock GitHub issues by keyword or tag."""
    query_lower = query.lower()
    results = [
        issue for issue in GITHUB_ISSUES
        if query_lower in issue["title"].lower() or any(query_lower in tag.lower() for tag in issue["tags"])
    ]
    return json.dumps(results if results else [{"message": "No matching GitHub issues found."}])

if __name__ == "__main__":
    mcp.run()