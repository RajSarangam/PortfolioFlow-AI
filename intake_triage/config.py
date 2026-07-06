"""Central configuration for the Program Intake Triage Agent.

Keeping model name and paths in one place makes the agent easy to retune
without editing every sub-agent file.
"""
import os

# Gemini model served via Google AI Studio.
# Swap to "gemini-2.0-flash" if you hit availability/rate issues on your key.
MODEL = os.environ.get("TRIAGE_MODEL", "gemini-2.5-flash")

# Path to the synthetic portfolio dataset that the tools query.
# Resolved relative to the repo root so it works whether you run from a
# notebook (cwd = repo root) or via `adk run`.
PORTFOLIO_PATH = os.environ.get(
    "PORTFOLIO_PATH",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "portfolio.json"),
)

# Sampling temperature for all agents. 0 makes the pipeline deterministic:
# the same request yields the same scores and routing every run -- important
# for a governance process and for a reproducible demo/video.
TEMPERATURE = float(os.environ.get("TRIAGE_TEMPERATURE", "0"))
