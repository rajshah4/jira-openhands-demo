# Demo Runbook

This runbook reproduces the Jira to OpenHands SDLC automation demo.

## 1. Prepare The Target Repo

Use the Petstore app repo:

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

## 2. Create The Jira Ticket

Use the main ticket from:

```text
examples/sparse-budget-ticket.md
```

The ticket should not name the repo, file, API parameter, or implementation
approach.

## 3. Trigger OpenHands

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

## 4. Watch The Agent

In the OpenHands conversation, show the agent:

- reading the Jira issue
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

## 5. Review The PR

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

## 6. Return To Jira

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

## 7. Human-In-The-Loop Variant

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

## 8. Cleanup

After rehearsal:

- close or mark demo Jira tickets as complete
- close unneeded draft PRs
- keep private run logs local
- do not commit secrets, webhook payloads with private data, or one-off logs
