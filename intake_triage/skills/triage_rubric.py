"""Triage rubric -- the codified 'agent skill'.

This module is the reusable scoring skill the Triage Scorer agent relies on.
Two halves:
  1) RUBRIC_TEXT  -- the instruction the LLM follows to assign 1-5 scores.
  2) score_to_tier() -- a *deterministic* helper that turns those scores into a
     priority tier. Keeping the tier math in plain Python (not the LLM) makes
     the output reproducible and auditable, which is exactly what you want for
     a governance-style intake process.
"""

# ---- The rubric the scorer applies (value / effort / risk / strategic fit) ----
RUBRIC_TEXT = """
Score the request on FOUR dimensions, each 1-5 (integers only):

VALUE (business impact if delivered)
  1 = negligible, 3 = meaningful for one team, 5 = material enterprise-wide impact
EFFORT (size of build; NOTE: higher score = MORE effort = worse)
  1 = days, 3 = a few sprints, 5 = a multi-quarter program
RISK (delivery + compliance + dependency risk)
  1 = trivial/low, 3 = moderate, 5 = high (regulatory, security, heavy dependencies)
STRATEGIC_ALIGNMENT (fit to stated portfolio priorities)
  1 = off-strategy, 3 = adjacent, 5 = directly on a top priority

Be conservative. If the request lacks the information needed to score a
dimension, pick the midpoint (3) and add that dimension to "missing_info".
"""


def score_to_tier(value: int, effort: int, risk: int, alignment: int) -> dict:
    """Map four 1-5 scores to a priority tier deterministically.

    Returns a dict with the computed priority score, tier, and a short reason.
    Formula favors high value + alignment, penalizes effort + risk.
    """
    # Weighted: value and alignment pull priority up; effort and risk pull it down.
    priority_score = (value * 2) + (alignment * 2) - effort - risk  # range ~ -6..18

    if priority_score >= 12:
        tier, reason = "P0", "high value/alignment, manageable effort & risk"
    elif priority_score >= 8:
        tier, reason = "P1", "strong candidate, worth scheduling soon"
    elif priority_score >= 4:
        tier, reason = "P2", "valuable but not urgent; backlog it"
    else:
        tier, reason = "P3", "low priority or high cost/risk; defer or decline"

    return {"priority_score": priority_score, "tier": tier, "tier_reason": reason}
