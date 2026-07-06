"""Sub-agent 1: Intake Parser.

Turns a free-text or form request into a structured record. Writes its result
to session state under 'parsed_request' so the next agent in the pipeline can
read it via {parsed_request} in its own instruction.
"""
from google.adk.agents import Agent
from google.genai import types as gt
from .. import config

intake_parser = Agent(
    name="intake_parser",
    model=config.MODEL,
    description="Converts a raw project request into a structured intake record.",
    instruction="""
You are the Intake Parser for an enterprise program-management office.

Read the user's raw request (free text or a pasted form) and extract a
structured record. Do NOT evaluate or score it -- only parse what is present.

Return ONLY a JSON object with these fields (use null or [] when unknown):
{
  "requestor": string | null,
  "business_unit": string | null,
  "problem_statement": string,
  "desired_outcome": string | null,
  "urgency": "low" | "medium" | "high" | null,
  "rough_size": "small" | "medium" | "large" | null,
  "dependencies": [string],
  "keywords": [string],          // 3-8 short terms for duplicate/dependency search
  "missing_info": [string]       // fields a reviewer would need but weren't provided
}

Output the JSON only -- no prose, no code fences.
""",
    generate_content_config=gt.GenerateContentConfig(temperature=config.TEMPERATURE),
    output_key="parsed_request",  # -> session.state["parsed_request"]
)
