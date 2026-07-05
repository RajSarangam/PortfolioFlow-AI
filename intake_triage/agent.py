"""Root orchestrator for the Program Intake Triage Agent.

This is a deterministic three-stage pipeline:

    Intake Parser  ->  Triage Scorer  ->  Router / Capacity Check

Each stage writes its structured JSON to session state under its output_key,
and the next stage reads it. A SequentialAgent guarantees the order runs the
same way every time -- important for a governance workflow and for a clean,
repeatable demo.

The human-in-the-loop guardrail is applied to the final output *after* the run
(see enforce_human_in_the_loop in guardrails.py and the demo notebook), so the
pipeline can never emit an autonomous approve/reject decision.

Exported as `root_agent` so it also works with `adk run intake_triage`.
"""
from google.adk.agents import SequentialAgent

from .sub_agents.intake_parser import intake_parser
from .sub_agents.triage_scorer import triage_scorer
from .sub_agents.router_capacity import router_capacity

root_agent = SequentialAgent(
    name="program_intake_orchestrator",
    description="Triages an enterprise program request: parse -> score -> route, "
                "always producing a human-reviewed recommendation.",
    sub_agents=[intake_parser, triage_scorer, router_capacity],
)
