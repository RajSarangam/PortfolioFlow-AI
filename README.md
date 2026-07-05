# Program Intake Triage Agent

A multi-agent AI system (built on **Google ADK-Python** + **Gemini**) that turns a raw
enterprise program request into a **structured, human-reviewed routing recommendation** —
in seconds instead of the hours a program manager spends triaging manually.

> **Capstone:** *AI Agents — Intensive Vibe Coding Capstone Project* · Track: **Agents for Business**

---

## The problem

In an enterprise program-management office, intake requests arrive as unstructured emails or
half-filled forms. A PM has to read each one, classify it, size the effort, check it against
the existing portfolio for duplicates and dependencies, and decide where it should go. It's
slow, inconsistent, and easy to get wrong when the portfolio is large.

## What the agent does

A deterministic three-stage pipeline under one orchestrator:

```
        ┌────────────────────────── program_intake_orchestrator (SequentialAgent) ──────────────────────────┐
        │                                                                                                    │
  raw   │   ┌───────────────┐      ┌────────────────┐      ┌──────────────────────────┐                      │   human-reviewed
 request├──▶│ Intake Parser │ ───▶ │ Triage Scorer  │ ───▶ │ Router / Capacity Check  │ ──▶ guardrail layer ─┼──▶ recommendation
        │   └───────────────┘      └────────────────┘      └──────────────────────────┘                      │   (+ confidence, flags)
        │     parsed_request         triage_assessment        routing_recommendation                         │
        └────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                          (session state passed stage → stage)
```

1. **Intake Parser** — converts free text into a structured record (requestor, business unit,
   problem, desired outcome, urgency, rough size, dependencies, keywords, missing info).
2. **Triage Scorer** — applies a fixed rubric (the *agent skill*) to score value, effort, risk,
   and strategic alignment, and flags likely duplicates or gaps.
3. **Router / Capacity Check** — uses custom tools to query the portfolio for capacity and
   related work, then recommends a route: `approve_to_backlog`, `needs_more_info`,
   `route_to_team`, or `defer`.

### The guardrail rule

**The agent never auto-approves or auto-rejects.** Every run ends in the guardrail layer, which
produces a *recommendation* with a confidence level and explicit review flags, stamped
`decision_authority: human` and `auto_action_taken: false`. A person makes the call.

---

## Concepts demonstrated

| Course concept | Where in the code |
|---|---|
| **Multi-agent system (ADK)** | `intake_triage/agent.py` — `SequentialAgent` over 3 specialists |
| **Sessions & state management** | each sub-agent's `output_key` writes to session state, read downstream via `{state_key}` |
| **Agent skills** | `intake_triage/skills/triage_rubric.py` — codified rubric + deterministic tier mapping |
| **Security / guardrail layer** | `intake_triage/guardrails.py` — input screening, tool-call guard, human-in-the-loop enforcement |
| **MCP server integration** *(optional upgrade)* | `mcp_server/portfolio_mcp_server.py` |

The core pipeline already demonstrates **four** concepts out of the box — comfortably past the
three-concept minimum. The MCP server is a ready-made fifth.

---

## Repo structure

```
program-intake-triage-agent/
├── intake_triage/
│   ├── agent.py                 # root orchestrator (exports root_agent)
│   ├── config.py                # model name + data path
│   ├── guardrails.py            # security / human-in-the-loop layer
│   ├── skills/triage_rubric.py  # the scoring rubric (agent skill)
│   ├── sub_agents/              # intake_parser, triage_scorer, router_capacity
│   └── tools/portfolio_tools.py # custom capacity + duplicate-scan tools
├── data/portfolio.json          # SYNTHETIC portfolio (teams + active projects)
├── mcp_server/portfolio_mcp_server.py   # optional MCP upgrade
├── notebooks/kaggle_demo.ipynb  # runnable demo (clone → run → guardrail)
├── requirements.txt
└── LICENSE                      # CC-BY 4.0 (required by the competition)
```

---

## Run it (Kaggle + GitHub combo)

**On Kaggle:**
1. Push this repo to a **public** GitHub repository.
2. New Kaggle Notebook → **Add-ons → Secrets** → add `GOOGLE_API_KEY` (your AI Studio key).
3. Open `notebooks/kaggle_demo.ipynb`, set your repo URL in the clone cell, and Run All.

**Locally:**
```bash
pip install -r requirements.txt
export GOOGLE_API_KEY="your-ai-studio-key"
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
adk run intake_triage          # or open the notebook
```

The model defaults to `gemini-2.5-flash`; override with `TRIAGE_MODEL=gemini-2.0-flash` if needed.

---

## Notes

- **Data is 100% synthetic.** `portfolio.json` contains no real customer, employee, or program
  data. The business framing reflects real enterprise program-management workflows; no specific
  metrics or outcomes are claimed.
- **License:** CC-BY 4.0, as required for competition submissions (see `LICENSE`).
- **Before you submit, verify on the competition's Overview → Timeline and rules pages:**
  (1) the exact submission deadline, (2) the scoring rubric / category weights, and
  (3) the accepted list of key concepts. These live on the competition site, not in the repo.
