#!/usr/bin/env python3
"""Clone/search candidate repos to make demo discovery visible.

This script intentionally avoids GitHub code-search indexing. It fetches the
candidate repos configured in a small JSON catalog and searches the checked-out
content locally for terms from the Jira ticket plus repo-specific hints.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path


TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".py",
    ".json",
    ".ndjson",
    ".toml",
    ".yaml",
    ".yml",
    ".ini",
    ".cfg",
    ".html",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
}

SKIP_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
}

DOMAIN_TERMS = {
    "afford",
    "affordable",
    "adoption",
    "budget",
    "catalog",
    "fee",
    "filter",
    "log",
    "price",
    "search",
}

STOPWORDS = {
    "agent",
    "asking",
    "before",
    "context",
    "demo",
    "description",
    "details",
    "docs",
    "expected",
    "from",
    "keep",
    "main",
    "need",
    "needs",
    "notes",
    "path",
    "presenter",
    "should",
    "summary",
    "support",
    "that",
    "they",
    "this",
    "text",
    "ticket",
    "with",
}


@dataclass
class Match:
    path: str
    score: int
    terms: list[str]
    snippet: str


@dataclass
class RepoResult:
    name: str
    url: str
    ref: str | None
    score: int = 0
    matches: list[Match] = field(default_factory=list)
    error: str | None = None


def run(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def read_issue(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def extract_terms(issue_text: str, extra_terms: list[str]) -> list[str]:
    words = {
        word.lower()
        for word in re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", issue_text)
        if word.lower() not in STOPWORDS
    }
    words.update(DOMAIN_TERMS)
    words.update(term.lower() for term in extra_terms if term.strip())
    return sorted(words)


def clone_repo(repo: dict, destination: Path) -> str | None:
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


def iter_text_files(root: Path):
    for current_root, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        current = Path(current_root)
        for filename in files:
            path = current / filename
            if path.name in {"AGENTS.md", "SKILL.md"} or path.suffix.lower() in TEXT_EXTENSIONS:
                yield path


def score_file(path: Path, text: str, terms: list[str], root: Path) -> Match | None:
    lower = text.lower()
    found = [term for term in terms if term and term in lower]
    if not found:
        return None

    rel = path.relative_to(root).as_posix()
    score = len(set(found))
    if rel.startswith("docs/") or "/docs/" in rel:
        score += 4
    if "log" in rel:
        score += 4
    if "skill" in rel.lower() or rel == "AGENTS.md":
        score += 3
    if "test" in rel:
        score += 2
    if "catalog" in rel.lower() or "search" in rel.lower():
        score += 3

    snippet = ""
    for line in text.splitlines():
        clean = line.strip()
        if clean and any(term in clean.lower() for term in found):
            snippet = clean[:220]
            break

    return Match(path=rel, score=score, terms=sorted(set(found)), snippet=snippet)


def search_repo(repo: dict, workdir: Path, terms: list[str], max_matches: int) -> RepoResult:
    result = RepoResult(name=repo.get("name") or repo["url"], url=repo["url"], ref=repo.get("ref"))
    repo_dir = workdir / re.sub(r"[^A-Za-z0-9_.-]+", "-", result.name.lower()).strip("-")
    clone_warning = clone_repo(repo, repo_dir)
    if clone_warning and not repo_dir.exists():
        result.error = clone_warning
        return result
    if clone_warning:
        result.error = clone_warning

    matches: list[Match] = []
    for path in iter_text_files(repo_dir):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        match = score_file(path, text, terms, repo_dir)
        if match:
            matches.append(match)

    matches.sort(key=lambda item: item.score, reverse=True)
    result.matches = matches[:max_matches]
    result.score = sum(match.score for match in result.matches)
    return result


def print_results(results: list[RepoResult]) -> None:
    print("Live discovery results")
    print("======================")
    for index, result in enumerate(results, start=1):
        ref = f" @ {result.ref}" if result.ref else ""
        print(f"\n{index}. {result.name}{ref}")
        print(f"   {result.url}")
        print(f"   score: {result.score}")
        if result.error:
            print(f"   note: {result.error}")
        if not result.matches:
            print("   no matching files found")
            continue
        for match in result.matches:
            term_list = ", ".join(match.terms[:10])
            print(f"   - {match.path} (score {match.score}; terms: {term_list})")
            if match.snippet:
                print(f"     {match.snippet}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run live repository discovery for the Jira/OpenHands demo.")
    parser.add_argument("--catalog", type=Path, required=True, help="Path to repo catalog JSON.")
    parser.add_argument("--issue", type=Path, required=True, help="Path to a Jira ticket markdown/text file.")
    parser.add_argument("--term", action="append", default=[], help="Extra search term. Repeat as needed.")
    parser.add_argument("--max-repos", type=int, default=10, help="Maximum candidate repos to search.")
    parser.add_argument("--max-matches", type=int, default=5, help="Maximum file matches to show per repo.")
    parser.add_argument("--workdir", type=Path, help="Directory for cloned repos. Defaults to a temp dir.")
    parser.add_argument("--keep-workdir", action="store_true", help="Keep temporary clones after the search.")
    args = parser.parse_args()

    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    repos = catalog.get("repos", [])[: args.max_repos]
    if not repos:
        print("catalog contains no repos", file=sys.stderr)
        return 1

    if shutil.which("git") is None:
        print("git is required", file=sys.stderr)
        return 1

    terms = extract_terms(read_issue(args.issue), args.term)
    if args.workdir:
        workdir = args.workdir
        workdir.mkdir(parents=True, exist_ok=True)
        cleanup = False
    else:
        workdir = Path(tempfile.mkdtemp(prefix="jira-openhands-discovery-"))
        cleanup = not args.keep_workdir

    try:
        results = [search_repo(repo, workdir, terms, args.max_matches) for repo in repos]
        results.sort(key=lambda item: item.score, reverse=True)
        print_results(results)
        if args.keep_workdir or args.workdir:
            print(f"\nclones kept at: {workdir}")
    finally:
        if cleanup:
            shutil.rmtree(workdir, ignore_errors=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
