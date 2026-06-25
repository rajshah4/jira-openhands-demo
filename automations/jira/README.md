# Jira Automation Template

This folder contains the prompt-preset automation shape for the Jira to
OpenHands demo.

The preferred production path is:

```text
Jira issue-created webhook
-> OpenHands custom webhook source
-> prompt-preset automation
-> OpenHands agent conversation
-> GitHub draft PR
-> Jira completion comment
```

## Trigger Contract

The Jira webhook should send the raw Jira payload to a custom OpenHands webhook
source, for example `jira-direct`.

Recommended event key:

```text
webhookEvent
```

Expected issue-created event:

```text
jira:issue_created
```

Recommended filter:

```text
issue.fields.project.key == 'KAN' && issue.fields.issuetype.name == 'Task'
```

Adjust the project key and issue type for the customer environment.

## Registering The Automation

Use `automation.prompt-preset.example.json` as the starting point. Replace:

- `PROJECT_KEY`
- `TARGET_REPO_URL`
- `TARGET_BASE_BRANCH`
- Jira site/project details in the prompt
- any customer-specific docs/log locations

Then register with the OpenHands automation prompt preset endpoint in the
customer's Rajistics/OpenHands instance.

Do not put secrets in this repo. The automation should read Jira/GitHub/Teams
credentials from the OpenHands secret store.

## Presenter Replay

If webhook delivery is not ready, the presenter can still run the same prompt as
a one-off OpenHands/Rajistics automation against a known Jira issue. Be explicit
when doing this: presenter replay validates the agent behavior, while the direct
webhook path validates event delivery.
