"""Sub-agent 2: Triage Scorer.

Applies the codified rubric (the 'agent skill') to the parsed request and
assigns 1-5 scores plus a priority tier. Reads {parsed_request} from state and
writes its result to 'triage_assessment'.
"""
from google.adk.agents import Agent
from google.genai import types as gt
from .. import config
from ..skills.triage_rubric import RUBRIC_TEXT

triage_scorer = Agent(
    name="triage_scorer",
    model=config.MODEL,
    description="Scores a parsed request on value, effort, risk, and strategic alignment.",
    instruction=f"""
You are the Triage Scorer. Here is the parsed request to evaluate:

{{parsed_request}}

Apply this rubric exactly:
{RUBRIC_TEXT}

Then return ONLY a JSON object:
{{
  "scores": {{ "value": int, "effort": int, "risk": int, "strategic_alignment": int }},
  "rationale": {{ "value": string, "effort": string, "risk": string, "strategic_alignment": string }},
  "missing_info": [string],     // dimensions you had to assume (scored 3 due to gaps)
  "likely_duplicate": boolean   // true if the problem sounds like existing work
}}

Do not compute the priority tier yourself -- a downstream step does that
deterministically. Output the JSON only, no prose, no code fences.
""",
    generate_content_config=gt.GenerateContentConfig(temperature=config.TEMPERATURE),
    output_key="triage_assessment",  # -> session.state["triage_assessment"]
)
