"""Custom tools for the Router / Capacity Check agent.

These are plain Python functions. ADK automatically turns them into callable
tools for the agent based on their signature and docstring, so keep the
docstrings accurate -- the model reads them to decide how to call each tool.

Both tools read the synthetic portfolio.json (the 'mock source'). The capacity
tool is the natural place to later swap in a live MCP server -- see
mcp_server/portfolio_mcp_server.py.
"""
import json
from .. import config


def _load_portfolio() -> dict:
    """Load the synthetic portfolio dataset from disk."""
    with open(config.PORTFOLIO_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def lookup_capacity(team_name: str) -> dict:
    """Look up current delivery capacity for a team.

    Args:
        team_name: Name of the team to check (e.g. "Platform Engineering").
            Matching is case-insensitive and partial.

    Returns:
        A dict with the team's weekly capacity, committed and available points,
        and a simple capacity_state of "open", "tight", or "full". If the team
        is not found, returns the list of valid team names so the caller can
        retry.
    """
    portfolio = _load_portfolio()
    needle = team_name.strip().lower()

    for team in portfolio["teams"]:
        if needle in team["name"].lower():
            available = team["available_points"]
            if available >= 8:
                state = "open"
            elif available >= 3:
                state = "tight"
            else:
                state = "full"
            return {
                "found": True,
                "team": team["name"],
                "weekly_capacity_points": team["weekly_capacity_points"],
                "committed_points": team["committed_points"],
                "available_points": available,
                "capacity_state": state,
                "focus": team["focus"],
            }

    # Not found: hand back the valid options instead of guessing.
    return {
        "found": False,
        "requested": team_name,
        "valid_teams": [t["name"] for t in portfolio["teams"]],
    }


def find_related_projects(keywords: str) -> dict:
    """Scan active projects for likely duplicates or dependencies.

    Args:
        keywords: Space- or comma-separated keywords pulled from the request
            (e.g. "salesforce customer churn"). Matching is keyword overlap
            against each project's name, business unit, and tags.

    Returns:
        A dict listing any related projects with an overlap_score, so the agent
        can flag potential duplication or cross-team dependencies for a human
        to review. An empty list means no obvious overlap was found.
    """
    portfolio = _load_portfolio()
    # Normalize the incoming keywords into a clean set of terms.
    terms = {t.strip().lower() for t in keywords.replace(",", " ").split() if t.strip()}

    related = []
    for proj in portfolio["active_projects"]:
        haystack = " ".join(
            [proj["name"], proj["business_unit"], proj["team"]] + proj["keywords"]
        ).lower()
        # Count how many of the request's terms show up in this project.
        overlap = sorted(t for t in terms if t in haystack)
        if overlap:
            related.append({
                "id": proj["id"],
                "name": proj["name"],
                "team": proj["team"],
                "status": proj["status"],
                "overlap_score": len(overlap),
                "matched_terms": overlap,
            })

    # Strongest overlaps first.
    related.sort(key=lambda r: r["overlap_score"], reverse=True)
    return {"related_count": len(related), "related_projects": related}
