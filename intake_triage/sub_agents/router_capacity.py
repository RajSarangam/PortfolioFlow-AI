"""Sub-agent 3: Router / Capacity Check.

Uses the portfolio tools to check team capacity and look for duplicate or
dependent work, then recommends a route. Reads {parsed_request} and
{triage_assessment} from state and writes 'routing_recommendation'.

The before_tool_callback wires in the guardrail layer for every tool call.
"""
from google.adk.agents import Agent
from google.genai import types as gt
from .. import config
from ..tools.portfolio_tools import lookup_capacity, find_related_projects
from ..guardrails import tool_guardrail

router_capacity = Agent(
    name="router_capacity",
    model=config.MODEL,
    description="Checks portfolio capacity and duplicates, then recommends a route.",
    instruction="""
You are the Router / Capacity Check agent.

Inputs available to you:
- Parsed request: {parsed_request}
- Triage assessment: {triage_assessment}

Your job:
1. Call find_related_projects with the request's keywords to detect possible
   duplicates or cross-team dependencies.
2. Decide which team most likely owns this work, then call lookup_capacity for
   that team to see if there is room.
3. Recommend ONE route. You are advisory only -- recommend, never decide.

Return ONLY a JSON object:
{
  "recommendation": "approve_to_backlog" | "needs_more_info" | "route_to_team" | "defer",
  "target_team": string | null,
  "capacity_state": "open" | "tight" | "full" | "unknown",
  "related_projects": [ { "id": string, "name": string, "overlap_score": int } ],
  "reasoning": string,
  "open_questions": [string]   // what a human should confirm before acting
}

Rules:
- If the request is missing key info, recommend "needs_more_info".
- If a strong duplicate exists, say so in reasoning and recommend "needs_more_info"
  or "defer" rather than approving parallel work.
- If the target team is "full", lean toward "defer" or flag the capacity conflict.
Output the JSON only, no prose, no code fences.
""",
    tools=[find_related_projects, lookup_capacity],
    before_tool_callback=tool_guardrail,   # guardrail runs on every tool call
    generate_content_config=gt.GenerateContentConfig(temperature=config.TEMPERATURE),
    output_key="routing_recommendation",   # -> session.state["routing_recommendation"]
)
