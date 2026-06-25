# Jira to OpenHands SDLC Automation Demo

**Sparse Jira ticket -> OpenHands automation -> live discovery -> log evidence -> code, tests, PR, and Jira evidence.**

This repo is a customer-facing demo kit for reproducing a Jira-native
OpenHands workflow. It is not the application repo and it is not a work log.
It contains the steps, prompt template, OpenHands skill, Jira ticket examples,
and presenter runbook needed to understand and reproduce the demo.

The target application for the canonical run is
[`rajshah4/sdlc-automation-github-demo`](https://github.com/rajshah4/sdlc-automation-github-demo),
but the demo should not feel like the agent was simply handed that answer. The
kit includes a live discovery step that searches candidate repositories and
shows why the Petstore repo is the right target.

## Demo Thesis

OpenHands can turn a short Jira ticket written in business language into a
normal engineering workflow without hiding work from the team.

The demo shows an agent that can:

- ingest a sparse Jira ticket
- use docs/wiki context and logs to understand the request
- identify the correct repository and files
- search structured logs for concrete request/response evidence
- make a bounded code change
- create or update tests
- open a draft PR for human review
- comment back to Jira with evidence, assumptions, and next steps
- stop and ask a human when the ticket is too ambiguous

The point is not "an agent wrote code." The point is that OpenHands can operate
inside the SDLC boundaries customers already use: Jira for intake and status,
GitHub for review, and human approval for merge.

## What The Audience Sees

1. A Jira task says only: "Families need to find pets in their budget."
2. OpenHands runs a discovery search across candidate repositories.
3. OpenHands searches structured service logs for a budget cap and response
   items.
4. OpenHands reads docs/wiki evidence to connect "budget" and "afford" to
   adoption fee filtering.
5. OpenHands finds the Petstore catalog search code in the selected repo.
6. OpenHands adds a max adoption fee filter and focused tests.
7. OpenHands opens a draft GitHub PR.
8. OpenHands comments back on Jira with the interpreted requirement, files
   changed, tests run, PR link, assumptions, and human-review next steps.
9. A second intentionally vague ticket demonstrates the safety behavior:
   OpenHands should ask for clarification instead of guessing.

## Architecture

```text
Jira task in KAN
        |
        v
Jira webhook or presenter replay
        |
        v
Rajistics / OpenHands automation
        |
        v
OpenHands agent with repo-local skill guidance
        |
        +--> Jira issue details
        +--> live repository discovery search
        +--> docs/wiki context
        +--> structured log evidence
        +--> selected GitHub repository
        |
        v
Draft PR + tests + Jira completion comment
```

## Repository Contents

| Path | Purpose |
| --- | --- |
| `automations/jira/` | Prompt-preset automation template and trigger notes for Jira events. |
| `discovery/` | Candidate repository catalog for live discovery. |
| `logs/` | Log-source catalog for realistic evidence search. |
| `skills/sparse-jira-ticket-to-pr/` | OpenHands skill that teaches the agent how to handle sparse Jira tickets safely. |
| `examples/` | Copy/paste Jira ticket examples for the main path and the human-in-loop path. |
| `docs/setup-checklist.md` | Prerequisites and configuration checklist. |
| `docs/demo-runbook.md` | Step-by-step reproduction flow. |
| `docs/customer-demo-script.md` | Presenter talk track. |
| `scripts/live_discovery_search.py` | Clones/searches candidate repos so discovery is visible and reproducible. |
| `scripts/live_log_search.py` | Searches structured log sources and highlights request/response evidence. |
| `scripts/check_demo_repo.sh` | Lightweight repo sanity check. |

Private working logs and scratch worktrees are ignored by git. They belong on
the presenter's machine, not in this public repo.

## Quick Start

Clone this demo kit and the target app repo:

```bash
git clone https://github.com/rajshah4/jira-openhands-demo.git
git clone https://github.com/rajshah4/sdlc-automation-github-demo.git
```

Validate the demo kit:

```bash
cd jira-openhands-demo
bash scripts/check_demo_repo.sh
```

Run the live discovery search:

```bash
python3 scripts/live_discovery_search.py \
  --catalog discovery/repo-catalog.example.json \
  --issue examples/sparse-budget-ticket.md
```

Run the live log evidence search:

```bash
python3 scripts/live_log_search.py \
  --catalog logs/log-sources.example.json \
  --issue examples/sparse-budget-ticket.md
```

Then follow:

- [Setup checklist](docs/setup-checklist.md)
- [Demo runbook](docs/demo-runbook.md)
- [Customer demo script](docs/customer-demo-script.md)

## Primary Ticket

Use this Jira task for the main path:

```text
Summary: Families need to find pets in their budget

Description:
Adoption counselors say families keep asking to see pets they can afford before
they visit. Can we make search support that?
```

The ticket intentionally avoids words like filter, API parameter, file name, or
repo name. OpenHands should discover those from context.

## Human-In-The-Loop Ticket

Use this task to show the safety behavior:

```text
Summary: People are confused by pet prices

Description:
This came up in the intake review. Can we fix it?
```

OpenHands should not pick a random interpretation. It should explain what is
ambiguous and ask a human whether the intended work is search filtering, fee
display copy, payment policy, or something else.

## OpenHands Pieces

This repo includes a reusable skill and a prompt-preset template:

- [Sparse Jira Ticket to PR skill](skills/sparse-jira-ticket-to-pr/SKILL.md)
- [Jira automation template](automations/jira/automation.prompt-preset.example.json)
- [Automation prompt](automations/jira/prompt.md)

Customers should be able to inspect these files and see how the behavior is
bounded. The agent is instructed to gather evidence, make the smallest safe
change, create tests, open a draft PR, and ask for help when context is missing.

The discovery and log scripts are intentionally simple and inspectable. They do
not rely on GitHub code-search indexing. The discovery script clones configured
candidate repos and ranks evidence. The log script searches configured
structured log sources, parses NDJSON events, and highlights field-level
evidence such as `budget_limit_dollars`, `max_adoption_fee_cents`, and
over-budget response items.

## Secrets And Live Systems

Do not commit secrets here.

Use the OpenHands/Rajistics secret store or local ignored `.env` files for:

- Jira API base URL
- Jira user/email
- Jira API token
- GitHub token or GitHub integration
- OpenHands API key
- Microsoft Teams webhook or connector details, if using the optional
  human-in-loop escalation

The public repo should contain reproducible setup and demo logic, not private
run logs, access tokens, webhook secrets, or one-off incident notes.

## Current Status

The agentic code-generation path has been validated through a Rajistics
OpenHands run against the Petstore demo app. The remaining integration work is
to make the direct Jira issue-created webhook path reliable enough for a live
customer demo without presenter replay.
