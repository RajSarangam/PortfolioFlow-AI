"""Security & governance guardrail layer.

The core rule of this agent: it NEVER auto-approves or auto-rejects a request.
It produces a *recommendation* for a human, with a confidence level and explicit
review flags. This module enforces that rule in three places:

  1) screen_request()          -- input screening (run before the agent).
  2) tool_guardrail()          -- guards every tool call (ADK before_tool_callback).
  3) enforce_human_in_the_loop -- post-processes the final output so no autonomous
                                  approve/reject decision can ever leave the system.
"""
from typing import Any, Optional

# Phrases that often signal a prompt-injection attempt in a free-text request.
_INJECTION_FLAGS = [
    "ignore previous", "ignore all previous", "disregard your instructions",
    "system prompt", "you are now", "act as", "auto-approve", "auto approve",
    "approve this automatically", "bypass review",
]


def screen_request(text: str) -> dict:
    """Lightweight input screening on the raw request text.

    Returns a dict of flags. This does not block the request -- it surfaces
    concerns for the human reviewer and lowers the confidence of the result.
    """
    lowered = (text or "").lower()
    injection_hits = [p for p in _INJECTION_FLAGS if p in lowered]

    # Very rough PII signal -- enough to flag for review, not to "detect" PII.
    pii_suspected = ("@" in lowered) or any(
        w in lowered for w in ["ssn", "social security", "passport", "credit card"]
    )

    flags = []
    if injection_hits:
        flags.append("possible_prompt_injection")
    if pii_suspected:
        flags.append("possible_pii_present")
    if len((text or "").strip()) < 20:
        flags.append("request_too_short_to_assess")

    return {
        "input_flags": flags,
        "injection_hits": injection_hits,
        "pii_suspected": pii_suspected,
    }


def tool_guardrail(tool: Any, args: dict, tool_context: Any) -> Optional[dict]:
    """ADK before_tool_callback. Runs before every tool call.

    Returning None lets the call proceed. Returning a dict short-circuits the
    tool and hands that dict back as the result -- which we use to block any
    call that looks tampered with. Here it simply allows reads and logs them.
    """
    # All current tools are read-only portfolio lookups, so we allow them.
    # This hook is where you'd block writes, enforce allow-lists, or rate-limit.
    print(f"[guardrail] tool call: {getattr(tool, 'name', tool)} args={args}")
    return None


def enforce_human_in_the_loop(routing: dict, review_flags: list) -> dict:
    """Wrap the router's output so it is always a recommendation, never an action.

    Guarantees the final object:
      - is labeled as advisory (decision_authority = 'human'),
      - records that no automated action was taken,
      - carries a confidence level derived from how many review flags exist,
      - lists every reason a human should look before anything happens.
    """
    flags = list(review_flags or [])

    # Confidence drops as unresolved concerns accumulate.
    if len(flags) == 0:
        confidence = "high"
    elif len(flags) <= 2:
        confidence = "medium"
    else:
        confidence = "low"

    # Normalize whatever the router proposed into a non-binding recommendation.
    recommendation = routing.get("recommendation") or routing.get("route") or "needs_more_info"

    return {
        "recommendation": recommendation,           # e.g. approve_to_backlog / needs_more_info / route_to_team / defer
        "decision_authority": "human",              # the agent never decides
        "auto_action_taken": False,                 # nothing was executed
        "human_review_required": True,              # always true, by design
        "confidence": confidence,
        "review_flags": flags,
        "router_detail": routing,                   # full reasoning, for the reviewer
    }
