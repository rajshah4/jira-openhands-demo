# Setup Checklist

Use this checklist to reproduce the Jira to OpenHands demo in a customer or
demo environment.

## Required Accounts

- Jira Cloud project where you can create issues and configure webhooks
- GitHub repository access for
  `rajshah4/sdlc-automation-github-demo` or a customer fork
- Rajistics/OpenHands instance with automations enabled
- OpenHands access to a model profile suitable for coding work

Optional:

- Microsoft Teams channel or webhook for human-in-loop escalation

## Repositories

Clone the demo kit:

```bash
git clone https://github.com/rajshah4/jira-openhands-demo.git
```

Clone the target app repo:

```bash
git clone https://github.com/rajshah4/sdlc-automation-github-demo.git
```

Choose a base branch in the target app repo that contains:

- repo-local OpenHands skill guidance
- docs/wiki context for pet affordability
- log fixture showing the budget/adoption-fee mismatch
- no pre-applied catalog fix, so the agent has real work to do

## Discovery Catalog

Review:

```text
discovery/repo-catalog.example.json
```

For a customer environment, replace the sample repos with likely application
repos, service repos, docs repos, or monorepo paths. Keep the candidate set
small enough for a live demo, usually 3-8 repos.

Run:

```bash
python3 scripts/live_discovery_search.py \
  --catalog discovery/repo-catalog.example.json \
  --issue examples/sparse-budget-ticket.md
```

The output should rank candidate repos and show matching files/snippets. Tune
repo hints until discovery looks like a realistic engineer search, not a magic
answer key.

## OpenHands Secrets

Store secrets in OpenHands/Rajistics, not in this repo.

Typical secret names:

```text
JIRA_API_BASE_URL
JIRA_EMAIL
JIRA_API_TOKEN
GITHUB_TOKEN
TEAMS_WEBHOOK_URL
```

The exact names can differ, but the automation prompt and skill should agree on
how to read them.

## Jira Webhook

Create a Jira webhook for issue-created events in the demo project.

Target:

```text
OpenHands custom webhook URL for source jira-direct
```

Event:

```text
jira:issue_created
```

Recommended scope:

```text
project = KAN
issue type = Task
```

Make sure the OpenHands webhook source expects the same event key expression and
signature header that Jira sends.

## OpenHands Automation

Start from:

```text
automations/jira/automation.prompt-preset.example.json
automations/jira/prompt.md
```

Register the prompt-preset automation in the Rajistics/OpenHands instance.

Check:

- trigger source matches the custom webhook source
- event key matches `jira:issue_created`
- filter matches the demo Jira project and issue type
- target repo URL and base branch are correct
- timeout is long enough for repo setup, code changes, tests, PR, and Jira
  comment

## Dry Run

Before the live Jira trigger:

1. Confirm the target app repo tests pass locally.
2. Confirm the OpenHands automation can clone the target repo.
3. Confirm Jira secrets can fetch the demo issue.
4. Confirm GitHub access can push a branch and open a draft PR.
5. Confirm Jira comment creation works.

If direct webhook delivery is not ready, use presenter replay and clearly label
it as replay rather than automatic event delivery.
