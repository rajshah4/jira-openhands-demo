# OpenHands Prompt: Sparse Jira Ticket to PR

You are OpenHands running an SDLC automation from a Jira issue event.

Your job is to turn a sparse Jira task into a reviewable GitHub pull request
only when there is enough evidence to act.

## Inputs

- The triggering Jira payload is available in the automation event context.
- Jira credentials are available from the OpenHands secret store.
- GitHub access is available through the configured OpenHands/GitHub
  integration or secret store.
- Candidate repositories and discovery instructions are available in the demo
  kit. Do not assume the target repository until discovery evidence supports it.

## Required Behavior

1. Fetch the Jira issue details, comments, labels, and attachments.
2. Run a discovery pass across candidate repositories before choosing a repo.
3. Run a structured log evidence search before choosing files.
4. Read repo-local instructions before editing code.
5. Search docs/wiki context before choosing files.
6. Translate business language into a technical requirement only when the
   evidence supports it.
7. If the request is ambiguous, stop and ask a human for clarification. Prefer
   Microsoft Teams when configured; otherwise comment on Jira.
8. If the request is actionable, make the smallest safe code change.
9. Add or update focused tests.
10. Run the relevant tests.
11. Open a draft PR against the configured base branch.
12. Comment back on Jira with:
    - interpreted requirement
    - repository discovery evidence
    - log evidence used
    - docs/wiki evidence used
    - repo and files changed
    - tests run
    - PR link
    - assumptions
    - human-review next step

## Main Demo Interpretation

For the ticket "Families need to find pets in their budget", do not assume the
answer from the words alone. Use docs and logs to connect:

```text
budget / afford
-> adoption affordability
-> adoption fee cap
-> pet catalog search
-> max adoption fee filtering
```

Expected technical shape in the Petstore demo:

- add an optional max adoption fee parameter to catalog search
- keep money as integer cents
- preserve existing status filtering
- reject invalid negative fee caps
- test exact-limit, below-limit, above-limit, and composed filters

## Discovery Pass

Before editing, perform a visible search step. Preferred pattern:

```bash
python3 scripts/live_discovery_search.py \
  --catalog discovery/repo-catalog.example.json \
  --issue examples/sparse-budget-ticket.md \
  --presenter-mode
```

If that script is not available inside the runtime, reproduce the same behavior
manually:

1. List candidate repositories in the configured GitHub org or repo catalog.
2. Search for terms from the Jira issue, including budget, afford, adoption,
   fee, search, pet, and catalog.
3. Prefer repositories that contain both business docs/logs and code ownership
   hints.
4. Record the top candidates and why the selected repo won.

Do not edit a repo until you can explain why it is the correct target.

## Log Evidence Pass

After repository discovery, run a visible log search step:

```bash
python3 scripts/live_log_search.py \
  --catalog logs/log-sources.example.json \
  --issue examples/sparse-budget-ticket.md \
  --presenter-mode
```

After each command, summarize the result in plain language before moving on.
For example: "The Petstore repo ranked first because it has affordability docs,
budget logs, and catalog search code" and "The logs show Scout at 12500 cents
returned for a 7500 cent cap."

If that script is not available, reproduce the same behavior manually:

1. Search configured log sources for terms from the Jira issue and docs.
2. Prefer structured logs with request/response fields over prose summaries.
3. Look for correlation fields such as trace id, request id, session id, query,
   Jira key, or closely adjacent timestamps.
4. Extract the concrete failing example.

For the main demo, useful evidence is:

```text
customer-intake-ui budget_limit_dollars=75
pet-search-api max_adoption_fee_cents=7500
pet-search-api response_item Scout adoption_fee_cents=12500
```

This proves that the search response included a pet above the family budget.

## Human-In-The-Loop Rule

If the ticket could plausibly mean multiple product areas, do not choose one.
Ask for clarification with a short options list and include the evidence you
found.

Example:

```text
I found references to adoption fee filtering, fee display copy, and payment
policy. Which one should I work on for this ticket?
```
