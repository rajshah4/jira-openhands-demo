#!/usr/bin/env python3
"""Search structured log sources for Jira/OpenHands demo evidence.

The script supports repo-hosted NDJSON, local NDJSON, and HTTP NDJSON sources.
It keeps the demo reproducible while preserving the feel of a real observability
step: search logs, parse structured events, correlate a request, and surface a
concrete failing example.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


STOPWORDS = {
    "description",
    "expected",
    "notes",
    "presenter",
    "summary",
    "that",
    "this",
    "ticket",
    "with",
}

DOMAIN_TERMS = {
    "adoption",
    "afford",
    "budget",
    "catalog",
    "fee",
    "filter",
    "price",
    "search",
}


@dataclass
class LogEvent:
    source: str
    path: str
    line_number: int
    data: dict[str, Any]
    score: int
    matched_terms: list[str] = field(default_factory=list)
    matched_fields: list[str] = field(default_factory=list)


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def extract_terms(text: str, extra_terms: list[str]) -> list[str]:
    words = {
        word.lower()
        for word in re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", text)
        if word.lower() not in STOPWORDS
    }
    words.update(DOMAIN_TERMS)
    words.update(term.lower() for term in extra_terms if term.strip())
    return sorted(words)


def clone_repo(repo: dict[str, Any], destination: Path) -> str | None:
    url = repo["url"]
    ref = repo.get("ref")
    command = ["git", "clone", "--depth", "1"]
    if ref:
        command.extend(["--branch", ref])
    command.extend([url, str(destination)])
    result = run(command)
    if result.returncode == 0:
        return None
    if ref:
        fallback = run(["git", "clone", "--depth", "1", url, str(destination)])
        if fallback.returncode == 0:
            return f"branch {ref!r} was unavailable; searched default branch"
        return (fallback.stderr or result.stderr).strip()
    return result.stderr.strip()


def source_paths(source: dict[str, Any], workdir: Path) -> tuple[list[Path], list[str]]:
    notes: list[str] = []
    source_type = source.get("type")
    if source_type == "repo_ndjson":
        repo = source["repo"]
        repo_name = re.sub(r"[^A-Za-z0-9_.-]+", "-", source["name"].lower()).strip("-")
        repo_dir = workdir / repo_name
        note = clone_repo(repo, repo_dir)
        if note:
            notes.append(note)
        if not repo_dir.exists():
            return [], notes
        paths: list[Path] = []
        for pattern in source.get("paths", []):
            paths.extend(Path(p) for p in glob.glob(str(repo_dir / pattern), recursive=True))
        return paths, notes

    if source_type == "local_ndjson":
        paths = []
        for pattern in source.get("paths", []):
            paths.extend(Path(p) for p in glob.glob(pattern, recursive=True))
        return paths, notes

    if source_type == "http_ndjson":
        url = source["url"]
        destination = workdir / f"{re.sub(r'[^A-Za-z0-9_.-]+', '-', source['name'].lower()).strip('-')}.ndjson"
        with urllib.request.urlopen(url, timeout=30) as response:
            destination.write_bytes(response.read())
        return [destination], notes

    notes.append(f"unsupported source type: {source_type}")
    return [], notes


def parse_ndjson(path: Path, source_name: str, terms: list[str], field_hints: list[str]) -> list[LogEvent]:
    events: list[LogEvent] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict):
            continue
        serialized = json.dumps(data, sort_keys=True).lower()
        matched_terms = [term for term in terms if term in serialized]
        matched_fields = [field for field in field_hints if field in data]
        if not matched_terms and not matched_fields:
            continue
        score = len(set(matched_terms)) + (2 * len(set(matched_fields)))
        if data.get("event") in {"search_submitted", "request_received", "response_item"}:
            score += 3
        if "budget_limit_dollars" in data or "max_adoption_fee_cents" in data:
            score += 5
        if "adoption_fee_cents" in data:
            score += 3
        events.append(
            LogEvent(
                source=source_name,
                path=path.as_posix(),
                line_number=line_number,
                data=data,
                score=score,
                matched_terms=sorted(set(matched_terms)),
                matched_fields=sorted(set(matched_fields)),
            )
        )
    return events


def find_over_budget(events: list[LogEvent]) -> list[str]:
    findings: list[str] = []
    active_cap: int | None = None
    active_query: str | None = None
    for event in sorted(events, key=lambda item: (item.data.get("timestamp", ""), item.line_number)):
        data = event.data
        if isinstance(data.get("budget_limit_dollars"), (int, float)):
            active_cap = int(float(data["budget_limit_dollars"]) * 100)
            active_query = str(data.get("query") or active_query or "")
            findings.append(
                f"budget cap observed: budget_limit_dollars={data['budget_limit_dollars']} -> {active_cap} cents"
            )
        if isinstance(data.get("max_adoption_fee_cents"), int):
            active_cap = int(data["max_adoption_fee_cents"])
            active_query = str(data.get("query") or active_query or "")
            findings.append(f"API request carried max_adoption_fee_cents={active_cap}")
        fee = data.get("adoption_fee_cents")
        if active_cap is not None and isinstance(fee, int) and fee > active_cap:
            pet_name = data.get("pet_name") or data.get("pet_id") or "unknown pet"
            query = data.get("query") or active_query
            suffix = f" for query {query!r}" if query else ""
            findings.append(f"over-budget response item: {pet_name} adoption_fee_cents={fee} > cap={active_cap}{suffix}")
    return findings


def compact_event(event: LogEvent) -> str:
    data = event.data
    fields = [
        "timestamp",
        "service",
        "event",
        "query",
        "budget_limit_dollars",
        "max_adoption_fee_cents",
        "pet_id",
        "pet_name",
        "adoption_fee_cents",
        "message",
    ]
    shown = {field: data[field] for field in fields if field in data}
    return json.dumps(shown, sort_keys=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Search structured log evidence for the Jira/OpenHands demo.")
    parser.add_argument("--catalog", type=Path, required=True, help="Path to log source catalog JSON.")
    parser.add_argument("--issue", type=Path, required=True, help="Path to a Jira ticket markdown/text file.")
    parser.add_argument("--term", action="append", default=[], help="Extra search term. Repeat as needed.")
    parser.add_argument("--max-events", type=int, default=8, help="Maximum matched events to print per source.")
    parser.add_argument("--workdir", type=Path, help="Directory for cloned repos/downloads. Defaults to a temp dir.")
    parser.add_argument("--keep-workdir", action="store_true", help="Keep temporary files after the search.")
    args = parser.parse_args()

    if shutil.which("git") is None:
        print("git is required", file=sys.stderr)
        return 1

    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    issue_text = args.issue.read_text(encoding="utf-8", errors="ignore")
    base_terms = extract_terms(issue_text, args.term)

    if args.workdir:
        workdir = args.workdir
        workdir.mkdir(parents=True, exist_ok=True)
        cleanup = False
    else:
        workdir = Path(tempfile.mkdtemp(prefix="jira-openhands-logs-"))
        cleanup = not args.keep_workdir

    try:
        print("Live log evidence")
        print("=================")
        all_events: list[LogEvent] = []
        for source in catalog.get("sources", []):
            print(f"\n{source.get('name', 'unnamed source')}")
            print("-" * len(source.get("name", "unnamed source")))
            terms = sorted(set(base_terms) | set(term.lower() for term in source.get("terms", [])))
            field_hints = source.get("field_hints", [])
            paths, notes = source_paths(source, workdir)
            for note in notes:
                print(f"note: {note}")
            if not paths:
                print("no log files found")
                continue
            source_events: list[LogEvent] = []
            for path in paths:
                source_events.extend(parse_ndjson(path, source.get("name", "source"), terms, field_hints))
            source_events.sort(key=lambda item: item.score, reverse=True)
            all_events.extend(source_events)
            if not source_events:
                print("no matching events found")
                continue
            print("matched events:")
            for event in source_events[: args.max_events]:
                print(f"- {Path(event.path).name}:{event.line_number} score={event.score}")
                print(f"  fields: {', '.join(event.matched_fields) or '-'}")
                print(f"  event: {compact_event(event)}")

        findings = find_over_budget(all_events)
        if findings:
            print("\nEvidence findings")
            print("-----------------")
            seen: set[str] = set()
            for finding in findings:
                if finding not in seen:
                    seen.add(finding)
                    print(f"- {finding}")
        if args.keep_workdir or args.workdir:
            print(f"\nlog workdir: {workdir}")
    finally:
        if cleanup:
            shutil.rmtree(workdir, ignore_errors=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
