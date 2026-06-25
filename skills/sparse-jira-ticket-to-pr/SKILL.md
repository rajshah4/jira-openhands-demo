---
name: sparse-jira-ticket-to-pr
description: Use when OpenHands receives a short Jira ticket and needs to determine whether it has enough context to locate the right repository, make a safe code change, add tests, open a PR, or ask a human for clarification.
triggers:
  - Jira ticket
  - sparse ticket
  - business language
  - open PR
  - ask human
---

# Sparse Jira Ticket to PR

This skill guides an OpenHands agent through a customer-facing SDLC automation:
a short Jira ticket becomes a bounded pull request only after the agent gathers
enough evidence.

## Operating Rule

Do not jump from the Jira title straight to code. First establish:

1. What business problem the ticket describes.
2. What docs/wiki context says about that language.
3. What logs or attached evidence prove the bug or requirement.
4. Which repository and files own the behavior.
5. Whether there is enough information to act safely.

If any of those are missing, ask a human instead of guessing.

## Workflow

1. Read the Jira issue.
   - summary
   - description
   - comments
   - labels
   - attachments
   - linked docs or incidents
2. Search the available docs/wiki context for business terms from the ticket.
3. Search logs or attached evidence for concrete request/response examples.
4. Identify the owning repository and files.
5. State the inferred requirement before editing.
6. Implement the smallest safe change.
7. Add or update focused tests.
8. Run tests and capture the exact command/results.
9. Open a draft PR.
10. Comment back to Jira with evidence and next steps.

## Evidence Standards

Good evidence:

- a doc that maps business terms to product behavior
- logs showing the failing or missing behavior
- repo-local instructions or ownership maps
- existing tests that define current behavior

Weak evidence:

- the ticket title alone
- a single vague complaint
- a guessed product area
- a code search hit with no business/log support

When evidence is weak, ask for clarification.

## Main Demo Mapping

For this demo, the ticket says:

```text
Families need to find pets in their budget
```

The expected inference is:

```text
budget / afford
-> adoption affordability
-> maximum adoption fee constraint
-> Petstore catalog search
-> max_adoption_fee_cents
```

The implementation should:

- keep adoption fees in integer cents
- add optional max adoption fee filtering
- preserve existing default availability filtering
- include pets at the exact budget limit
- exclude pets over the budget limit
- reject negative fee caps

## Human Clarification Pattern

If the ticket is too vague, post or send:

```text
I found more than one plausible interpretation and do not have enough evidence
to choose safely.

Options:
1. Search filtering by adoption fee
2. Fee display/copy changes
3. Payment or checkout policy

Which one should I work on?
```

Prefer Microsoft Teams when a Teams escalation channel is configured. Otherwise
comment on the Jira issue and mark the work as waiting for human input.

## Jira Completion Comment

After a successful PR, comment with:

- interpreted requirement
- docs/logs used
- repo and files changed
- tests run
- PR link
- assumptions
- human-review next step

Do not mark the work merged or deployed. The output is a draft PR for review.
