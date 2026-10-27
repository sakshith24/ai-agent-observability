from mcp.server.fastmcp import FastMCP

mcp = FastMCP("GitHub Assistant MCP")

@mcp.tool()
def search_github_issues(query: str) -> str:
    """Search GitHub issues for a given query string."""
    # Mock implementation for initial end-to-end testing
    mock_issues = [
        {"id": 101, "title": "Fix WebSocket reconnection bug", "state": "open"},
        {"id": 102, "title": "Optimize PostgreSQL connection pool", "state": "closed"}
    ]
    matched = [i for i in mock_issues if query.lower() in i["title"].lower()]
    return str(matched if matched else "No issues found.")

if __name__ == "__main__":
    mcp.run()