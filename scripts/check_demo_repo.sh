#!/usr/bin/env bash
set -euo pipefail

required_paths=(
  "README.md"
  "automations/jira/automation.prompt-preset.example.json"
  "automations/jira/prompt.md"
  "skills/sparse-jira-ticket-to-pr/SKILL.md"
  "docs/setup-checklist.md"
  "docs/demo-runbook.md"
  "docs/customer-demo-script.md"
  "examples/sparse-budget-ticket.md"
  "examples/needs-human-ticket.md"
)

missing=0
for path in "${required_paths[@]}"; do
  if [[ ! -e "$path" ]]; then
    echo "missing: $path"
    missing=1
  fi
done

if [[ "$missing" -ne 0 ]]; then
  exit 1
fi

echo "demo repo structure looks good"
