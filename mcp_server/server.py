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
def search_github_issues(
    query: str,
    status: str = "all"
) -> dict:
    """
    Search GitHub issues by keyword.

    Search matches against issue title, description and tags.
    Optionally filter by open or closed status.

    Args:
        query: Keyword to search for.
        status: Issue status: open, closed, or all.
    """
    query = query.strip().lower()
    status = status.strip().lower()

    if not query:
        return {
            "success": False,
            "error": "Search query cannot be empty."
        }

    if status not in ["open", "closed", "all"]:
        return {
            "success": False,
            "error": "Status must be open, closed, or all."
        }

    results = []

    for issue in GITHUB_ISSUES:

        # Match the query against title, description and tags
        searchable_text = (
            issue["title"] + " " +
            issue["description"] + " " +
            " ".join(issue["tags"])
        ).lower()

        matches_query = query in searchable_text

        # Check the requested issue status
        matches_status = (
            status == "all" or issue["status"] == status
        )

        if matches_query and matches_status:
            results.append(issue)

    return {
        "success": True,
        "query": query,
        "status": status,
        "count": len(results),
        "issues": results
    }


if __name__ == "__main__":
    mcp.run()
