"""Optional MCP server for the portfolio (capacity + duplicate lookup).

WHY THIS EXISTS
The default agent calls portfolio_tools.py directly, so it runs with zero MCP
setup. This file is the upgrade path: it exposes the SAME two lookups over the
Model Context Protocol, which lets you demonstrate the 'MCP server integration'
concept for extra depth in your writeup.

RUN IT (stdio transport):
    pip install mcp
    python mcp_server/portfolio_mcp_server.py

WIRE IT INTO THE ROUTER (replace the tools= line in router_capacity.py):
    from google.adk.tools.mcp_tool import MCPToolset, StdioServerParameters
    portfolio_mcp = MCPToolset(
        connection_params=StdioServerParameters(
            command="python",
            args=["mcp_server/portfolio_mcp_server.py"],
        )
    )
    # then: tools=[portfolio_mcp]
Check the exact MCPToolset import path against your installed ADK version
(`python -c "import google.adk.tools.mcp_tool as m; print(dir(m))"`), since it
has moved between releases.
"""
import json
import os

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("portfolio")

_PORTFOLIO_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "portfolio.json"
)


def _load():
    with open(_PORTFOLIO_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@mcp.tool()
def lookup_capacity(team_name: str) -> dict:
    """Return weekly capacity and availability for a team (case-insensitive, partial match)."""
    needle = team_name.strip().lower()
    for team in _load()["teams"]:
        if needle in team["name"].lower():
            available = team["available_points"]
            state = "open" if available >= 8 else "tight" if available >= 3 else "full"
            return {"found": True, "team": team["name"],
                    "available_points": available, "capacity_state": state}
    return {"found": False, "requested": team_name}


@mcp.tool()
def find_related_projects(keywords: str) -> dict:
    """Return active projects whose name/unit/tags overlap the given keywords."""
    terms = {t.strip().lower() for t in keywords.replace(",", " ").split() if t.strip()}
    related = []
    for proj in _load()["active_projects"]:
        haystack = " ".join([proj["name"], proj["business_unit"]] + proj["keywords"]).lower()
        overlap = [t for t in terms if t in haystack]
        if overlap:
            related.append({"id": proj["id"], "name": proj["name"],
                            "overlap_score": len(overlap)})
    related.sort(key=lambda r: r["overlap_score"], reverse=True)
    return {"related_count": len(related), "related_projects": related}


if __name__ == "__main__":
    # Default stdio transport -- works with ADK's MCPToolset(StdioServerParameters(...)).
    mcp.run()
