# Demo Runbook

This runbook reproduces the Jira to OpenHands SDLC automation demo.

## 1. Prepare Candidate Repos

The demo should show discovery before implementation. Start with a small
candidate repo catalog instead of handing the agent the answer.

Default catalog:

```text
discovery/repo-catalog.example.json
```

The canonical target app is:

```text
https://github.com/rajshah4/sdlc-automation-github-demo
```

Use a base branch that has the demo docs, logs, fixtures, and skill guidance,
but does not already contain the final catalog fix.

The branch should include:

- docs/wiki context for pet discovery affordability
- log evidence for budget/adoption-fee mismatch
- repo-local skill or references that map product areas to files
- tests for current catalog behavior

## 2. Run Discovery Once As Presenter

Before the live agent run, verify the discovery search produces a useful result:

```bash
python3 scripts/live_discovery_search.py \
  --catalog discovery/repo-catalog.example.json \
  --issue examples/sparse-budget-ticket.md
```

You should see the Petstore SDLC demo repo rank highly because it contains
matching business docs, log evidence, and catalog/search code hints.

This step is useful in the customer conversation:

```text
The agent is not being handed a file path. It first searches likely systems and
then explains why it picked this repository.
```

## 3. Create The Jira Ticket

Use the main ticket from:

```text
examples/sparse-budget-ticket.md
```

The ticket should not name the repo, file, API parameter, or implementation
approach.

## 4. Trigger OpenHands

Preferred:

```text
Jira issue-created webhook -> OpenHands custom webhook -> automation
```

Fallback for rehearsal:

```text
One-off Rajistics/OpenHands prompt automation against the known Jira issue
```

If using fallback, say so in the demo. It validates the agent workflow, not the
webhook delivery path.

## 5. Watch The Agent

In the OpenHands conversation, show the agent:

- reading the Jira issue
- running the live discovery search
- ranking candidate repositories
- finding docs/wiki context
- reading log evidence
- identifying the target repository
- locating catalog search code and tests
- explaining the inferred requirement before editing
- implementing the filter
- adding tests
- running tests
- opening a draft PR
- commenting back to Jira

## 6. Review The PR

The PR should show:

- bounded catalog code change
- focused test additions
- optional OpenSpec-style artifacts
- draft state for human review
- no automatic merge

The presenter message:

```text
OpenHands did the engineering legwork, but GitHub is still the review and merge
boundary.
```

## 7. Return To Jira

Show the completion comment:

- interpreted requirement
- docs/logs used
- files changed
- tests run
- PR link
- assumptions
- human-review next step

The presenter message:

```text
Jira remains the system of record. The agent brings evidence back to the ticket
instead of making the team hunt through a separate tool.
```

## 8. Human-In-The-Loop Variant

Create the ticket from:

```text
examples/needs-human-ticket.md
```

Expected behavior:

- OpenHands searches context.
- OpenHands finds multiple plausible interpretations.
- OpenHands asks for clarification instead of making a speculative change.
- Preferred escalation target is Microsoft Teams when configured.

The presenter message:

```text
The agent is useful because it knows when not to act.
```

## 9. Cleanup

After rehearsal:

- close or mark demo Jira tickets as complete
- close unneeded draft PRs
- keep private run logs local
- do not commit secrets, webhook payloads with private data, or one-off logs
