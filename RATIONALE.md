# Rationale — Program Intake Triage Agent

*AI Agents Intensive Capstone · Agents for Business · Raj Sarangam*

## Why this problem

I chose program intake triage because it's a bottleneck I've lived inside for years as a senior
program manager running enterprise portfolios across SAP, Workday, and Salesforce. Intake is the
front door to an EPMO: requests arrive as loose emails or half-filled forms, and someone has to
classify each one, size it, check it against everything already in flight, and decide where it
goes. Done at volume, that work becomes inconsistent and hard to audit — the tenth request of the
week gets a different read than the first, and duplicate efforts slip through because no one holds
the whole portfolio in their head. My prior work building AI-assisted intake-advisor workflows and
applying structured (CRAFT-style) prompting to request evaluation is what this agent formalizes
into a multi-agent system.

## Why a multi-agent pipeline instead of one prompt

I deliberately split the work into three specialists under one orchestrator — Intake Parser,
Triage Scorer, Router / Capacity Check — rather than asking a single model to do everything. Three
reasons. **Separation of concerns:** parsing, scoring, and routing are genuinely different tasks
with different inputs, and isolating them keeps each prompt focused and debuggable. **Auditability:**
each stage writes its structured JSON to session state, so a reviewer can see exactly what was
parsed, how it was scored, and why it was routed — not a single opaque verdict. **Determinism where
it matters:** the pipeline runs in a fixed order, and the priority-tier calculation is plain Python,
not the model, so the same scores always yield the same tier. That reproducibility is essential for
a governance process.

## Why human-in-the-loop is the spine, not a feature

Approving intake commits real delivery capacity and budget. That is an accountable human decision,
and it is not something a language model should execute autonomously. So the agent is advisory by
construction: every run ends in a guardrail layer that produces a *recommendation* with a
confidence level and explicit review flags, stamped so that no automated approve/reject can leave
the system. When information is thin or a request overlaps existing work, confidence drops and the
agent routes to "needs more info" rather than waving it through — surfacing the questions a human
should resolve first. This mirrors how real intake governance should work: the machine does the
tedious assembly; the person keeps the decision.

## Concepts demonstrated

- **Multi-agent system (ADK):** an orchestrator coordinating three specialist sub-agents.
- **Agent skills:** the value/effort/risk/alignment rubric, codified as a reusable skill with
  deterministic tier logic.
- **Security / guardrail layer:** input screening, per-tool-call guarding, and enforced
  human-in-the-loop output.
- **Sessions & state management:** structured JSON passed stage to stage via session state.
- **MCP server integration (MCP-ready):** the capacity/duplicate lookups are also exposed via an
  included MCP server, with the swap into the Router documented — a clean upgrade path.

## Authenticity note

The portfolio data is entirely synthetic and labeled as such; it contains no real customer,
employee, or program information. The business framing reflects genuine enterprise intake-governance
workflows I've worked in, but no specific customer outcomes or performance metrics are claimed.

> _[If I choose to quantify impact, I'll insert a real figure from my own EPMO experience here —
> e.g., typical manual triage time per request — rather than estimate one.]_
