# Program Intake Triage Agent
### Keeping a human in the loop for enterprise program intake
*AI Agents: Intensive Vibe Coding Capstone — Track: Agents for Business*
*Built with Google ADK-Python + Gemini (AI Studio)*

> _Thumbnail suggestion: the three-stage pipeline diagram below on a clean background, with the headline "Parse → Score → Route — human decides."_

---

## The problem

Every enterprise program-management office runs on intake. A request to build, buy, or change
something arrives — usually as a loose email or a half-completed form — and a program manager
has to make sense of it before anything can happen. That means reading it, classifying it,
sizing the effort, checking it against everything already in flight for duplicates and
dependencies, and deciding where it should go.

Done well, this is judgment work. Done at volume, it becomes a bottleneck: the same PM triaging
the tenth request of the week applies the rubric a little differently than they did on the
first, context gets lost, and duplicate efforts slip through because no one has the whole
portfolio in their head. The cost isn't just time — it's *inconsistency* and *poor auditability*
in a process that governs where an organization spends its delivery capacity.

This is the exact workflow I've spent years inside as a program manager across SAP, Workday, and
Salesforce environments — building AI-assisted intake-advisor patterns, structured (CRAFT-style)
prompting for request evaluation, and capacity-planning governance. The Program Intake Triage
Agent is that experience turned into a working multi-agent system.

## What it does

The agent takes one raw request and returns a **structured, human-reviewed routing
recommendation**. It is deliberately *advisory*: it does the tedious, error-prone assembly work
and hands a program manager a clean, consistent recommendation to approve — it never makes the
call itself.

It's a deterministic three-stage pipeline under one orchestrator:

```
        ┌───────────────── program_intake_orchestrator (SequentialAgent) ─────────────────┐
        │                                                                                  │
  raw   │   ┌──────────────┐    ┌───────────────┐    ┌──────────────────────┐              │  human-reviewed
request ├──▶│Intake Parser │──▶ │ Triage Scorer │──▶ │Router / Capacity Check│──▶ guardrail ┼─▶ recommendation
        │   └──────────────┘    └───────────────┘    └──────────────────────┘   layer      │  (+ confidence,
        │    parsed_request       triage_assessment     routing_recommendation              │     review flags)
        └──────────────────────────────────────────────────────────────────────────────────┘
                              (each stage passes structured JSON via session state)
```

1. **Intake Parser** — converts free text or a pasted form into a structured record: requestor,
   business unit, problem statement, desired outcome, urgency, rough size, dependencies, and the
   keywords needed for a duplicate search. It also lists what's *missing* rather than guessing.

2. **Triage Scorer** — applies a fixed rubric (value, effort, risk, strategic alignment; each
   1–5) implemented as a reusable **agent skill**, then a deterministic helper maps those scores
   to a priority tier (P0–P3). Keeping the tier math in plain Python rather than the model makes
   the outcome reproducible and auditable — the same scores always produce the same tier.

3. **Router / Capacity Check** — uses custom tools to query the portfolio for team capacity and
   for related/duplicate work, then recommends one route: *approve to backlog*, *needs more
   info*, *route to team*, or *defer*.

## The design rule: a human is always in the loop

The single most important design decision is what the agent is **not** allowed to do: it never
auto-approves and never auto-rejects. Approving work commits real delivery capacity and budget —
that is an accountable human decision, not something an LLM should execute autonomously.

So every run ends in a **guardrail layer** that assembles the final output as a *recommendation*,
stamped `decision_authority: human` and `auto_action_taken: false`, carrying a **confidence
level** and an explicit list of **review flags** (missing information, possible duplicates,
capacity conflicts, or input concerns). Confidence degrades as unresolved concerns accumulate,
so a thin or ambiguous request surfaces as low-confidence with visible reasons — it never gets
quietly waved through.

The guardrail also does lightweight input screening (basic prompt-injection and PII signals) and
guards every tool call, so the human reviewer sees not just a recommendation but *why* to look
before acting.

## Course concepts demonstrated

| Concept | How it shows up |
|---|---|
| **Multi-agent system (ADK)** | A `SequentialAgent` orchestrator coordinating three specialist sub-agents, each with a single responsibility. |
| **Agent skills** | The scoring rubric is a self-contained, reusable skill (`skills/triage_rubric.py`) — an instruction the model applies plus deterministic tier logic. |
| **Security / guardrail layer** | Input screening, per-tool-call guarding, and enforced human-in-the-loop output that can never emit an autonomous approve/reject. |
| **MCP server integration** | The capacity/duplicate lookups are also exposed over a Model Context Protocol server (`mcp_server/portfolio_mcp_server.py`) that the Router can consume in place of local tools. |
| **Sessions & state management** | Each stage writes structured JSON to session state; the next stage reads it — the mechanism that lets the pipeline compose. |

That's four demonstrated concepts in the core build (well past the required three), with MCP as a
ready fifth.

## How it works — a worked example

Given a request like *"Sales wants a single view of each customer pulling together Salesforce
records, support tickets, and product usage so reps can see churn risk — needed this quarter,
not sure who owns it,"* the pipeline:

- **parses** it into a structured record and flags that an owner and a hard deadline are missing;
- **scores** it (high value and strategic alignment, non-trivial effort and risk) and computes a
  priority tier;
- **checks the portfolio**, finds it overlaps existing customer-360 and customer-health work, and
  notes the likely owning team's capacity;
- **recommends** *needs more info* rather than approving parallel work — flagging the duplicate,
  the missing owner, and the capacity picture for a human to resolve.

The output is a single JSON object a PM can read in seconds, with every reason to pause made
explicit.

## Why it matters

The value here isn't replacing the program manager — it's giving them a consistent, portfolio-
aware first pass so their judgment is spent on decisions, not on assembly. In governance terms it
improves three things at once: **consistency** (the same rubric applied identically every time),
**auditability** (deterministic tiers and explicit flags, not a black-box verdict), and **speed
to a reviewable recommendation** — while keeping accountability firmly with a human.

> _[Placeholder — Raj to insert a real figure only if available: e.g., typical manual triage
> time per request in your EPMO, or intake volume per cycle. Do not estimate; leave out if no
> real number exists.]_

## Data and authenticity note

All portfolio data is **synthetic** (`data/portfolio.json`) and contains no real customer,
employee, or program information. The business framing reflects genuine enterprise intake-
governance workflows I've worked in; no specific customer outcomes or performance metrics are
claimed.

## Limitations and what's next

- **One input format by design.** The agent handles a single raw-request format; expanding to
  multiple structured intake forms is deliberately out of scope for this build.
- **Mock portfolio source.** Capacity and project data come from a synthetic file (or the local
  MCP server). A production version would connect the MCP server to a live PPM system.
- **Next steps:** wire the Router to the MCP server by default, add long-term memory so repeat or
  seasonal requests are recognized across cycles, and let a reviewer's accept/adjust decisions
  feed back into rubric calibration.

## Links

- **Code:** `[https://github.com/YOUR_USERNAME/program-intake-triage-agent]`
- **Demo video (~2 min):** `[add link]`

---

*Built by Raj Sarangam — Senior Program Manager (SAP · Workday · Salesforce) and CEO of ORP Soft —
as a Capstone submission for the AI Agents Intensive.*
