# Customer Demo Script

## Opening

Most engineering automation demos assume the ticket is already technical. Real
work usually starts messier than that. A customer, support person, or product
manager writes a short Jira issue in everyday language.

Today we will show OpenHands taking that kind of Jira issue and turning it into
a normal engineering artifact: a draft PR with tests and evidence.

## Scene 1: The Sparse Ticket

Show the Jira issue:

```text
Families need to find pets in their budget
```

Say:

```text
This does not say filter, API, max fee, repository, or file. That is the point.
The useful agent behavior is not just writing code. It is figuring out what
problem this maps to and whether there is enough evidence to act.
```

## Scene 2: Context Gathering

Show the agent running discovery search and then structured log search before it
edits code.

Say:

```text
OpenHands is not being handed a path. It first searches candidate repositories
using the language from the ticket. Then it searches structured logs for a real
request/response example. The docs connect budget language to adoption
affordability, and the logs show that a customer with a $75 budget received a
pet with a $125 adoption fee.
```

## Scene 3: Repo And File Discovery

Show the agent finding the target repo and catalog files.

Say:

```text
The Jira issue did not name a repo. OpenHands has to locate ownership before it
edits. In this demo, it identifies Petstore catalog search as the right surface.
```

Optional line:

```text
This is deliberately more realistic than a toy prompt. In customer settings,
the hard part is often finding the right system from an underspecified ticket.
```

## Scene 3A: Observability Evidence

Show the log search output.

Say:

```text
This is the moment that makes the demo feel real. The agent found an intake
event with budget_limit_dollars=75, a search request with
max_adoption_fee_cents=7500, and a response item where Scout had
adoption_fee_cents=12500. That is the evidence for the code change.
```

## Scene 4: Code And Tests

Show the diff and tests.

Say:

```text
The change is intentionally small: add an optional maximum adoption fee filter,
keep money in integer cents, preserve existing status filtering, and test the
boundary cases.
```

## Scene 5: Draft PR

Show the draft PR.

Say:

```text
The output is not an automatic merge. It is normal reviewable engineering work:
a branch, a PR, a test result, and assumptions a human can inspect.
```

## Scene 6: Jira Evidence

Return to Jira and show the completion comment.

Say:

```text
The loop closes in Jira. The ticket gets the interpreted requirement, evidence
used, files changed, tests run, PR link, and next step for human review.
```

## Scene 7: Human-In-The-Loop

Show the vague ticket:

```text
People are confused by pet prices
```

Say:

```text
This is where trust matters. If OpenHands cannot tell whether the request is
about search filtering, fee display copy, or payment policy, it should ask a
human. The goal is bounded autonomy, not confident guessing.
```

## Close

Say:

```text
OpenHands is the agentic layer inside the SDLC. Jira remains intake and status,
GitHub remains review and merge, and the agent does the context-gathering and
implementation work in between.
```
