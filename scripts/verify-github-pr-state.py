#!/usr/bin/env python3
"""Verify GitHub pull-request state before source mutation or merge decisions.

Supports live GitHub API verification and offline JSON fixtures for deterministic
qualification. The script fails closed on repository, state, head, or base
mismatches.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SHA_RE = re.compile(r"^[0-9a-fA-F]{7,64}$")

EXIT_REPOSITORY_MISMATCH = 40
EXIT_STATE_MISMATCH = 41
EXIT_HEAD_MISMATCH = 42
EXIT_BASE_MISMATCH = 43
EXIT_API_BLOCKED = 44
EXIT_CONFLICTING_PR = 45


def stop(message: str, code: int) -> None:
    print(f"STOP: {message}", file=sys.stderr)
    raise SystemExit(code)


def load_fixture(path: str) -> object:
    fixture = Path(path)
    if not fixture.is_file():
        stop(f"fixture not found: {fixture}", EXIT_API_BLOCKED)
    try:
        return json.loads(fixture.read_text(encoding="utf-8"))
    except Exception as exc:
        stop(f"cannot parse fixture JSON: {exc}", EXIT_API_BLOCKED)


def github_get(url: str) -> object:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        stop("GITHUB_TOKEN is required for live PR-state verification", EXIT_API_BLOCKED)
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "engineering-governance-pr-state-gate",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        stop(f"GitHub API HTTP {exc.code}: {exc.reason}", EXIT_API_BLOCKED)
    except Exception as exc:
        stop(f"GitHub API unavailable: {exc}", EXIT_API_BLOCKED)


def fetch_pr(repository: str, pr_number: int, fixture: str | None) -> object:
    if fixture:
        return load_fixture(fixture)
    return github_get(f"https://api.github.com/repos/{repository}/pulls/{pr_number}")


def fetch_open_prs_for_head(repository: str, head_branch: str, fixture: str | None) -> object:
    if fixture:
        return load_fixture(fixture)
    owner = repository.split("/", 1)[0]
    head = urllib.parse.quote(f"{owner}:{head_branch}", safe=":")
    return github_get(
        f"https://api.github.com/repos/{repository}/pulls?state=open&head={head}&per_page=100"
    )


def repo_identity(pr: dict) -> str | None:
    base = pr.get("base")
    if isinstance(base, dict):
        repo = base.get("repo")
        if isinstance(repo, dict):
            full_name = repo.get("full_name")
            if isinstance(full_name, str):
                return full_name
    return None


def verify_specific_pr(args: argparse.Namespace) -> None:
    if args.pr_number is None:
        stop("--pr-number is required in specific-PR mode", 2)
    if not args.expected_head or not SHA_RE.fullmatch(args.expected_head):
        stop("--expected-head must look like a Git SHA", 2)
    if not args.expected_base:
        stop("--expected-base is required in specific-PR mode", 2)

    payload = fetch_pr(args.repository, args.pr_number, args.fixture)
    if not isinstance(payload, dict):
        stop("PR response must be a JSON object", EXIT_API_BLOCKED)

    actual_repo = repo_identity(payload)
    if actual_repo != args.repository:
        stop(
            f"PR repository identity mismatch: expected={args.repository} actual={actual_repo}",
            EXIT_REPOSITORY_MISMATCH,
        )

    actual_number = payload.get("number")
    if actual_number != args.pr_number:
        stop(
            f"PR number mismatch: expected={args.pr_number} actual={actual_number}",
            EXIT_STATE_MISMATCH,
        )

    actual_state = payload.get("state")
    if actual_state != args.expected_state:
        stop(
            f"PR state mismatch: expected={args.expected_state} actual={actual_state}",
            EXIT_STATE_MISMATCH,
        )

    head = payload.get("head")
    actual_head = head.get("sha") if isinstance(head, dict) else None
    if actual_head != args.expected_head:
        stop(
            f"PR head mismatch: expected={args.expected_head} actual={actual_head}",
            EXIT_HEAD_MISMATCH,
        )

    base = payload.get("base")
    actual_base = base.get("ref") if isinstance(base, dict) else None
    if actual_base != args.expected_base:
        stop(
            f"PR base mismatch: expected={args.expected_base} actual={actual_base}",
            EXIT_BASE_MISMATCH,
        )

    print("PR_STATE_GATE=PASS")
    print(f"repository={args.repository}")
    print(f"pr_number={args.pr_number}")
    print(f"state={actual_state}")
    print(f"head_sha={actual_head}")
    print(f"base={actual_base}")


def verify_no_open_pr(args: argparse.Namespace) -> None:
    branch = args.expect_no_open_pr_for_head
    payload = fetch_open_prs_for_head(args.repository, branch, args.fixture)
    if not isinstance(payload, list):
        stop("open-PR response must be a JSON array", EXIT_API_BLOCKED)

    matching = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        base_repo = repo_identity(item)
        head = item.get("head")
        head_ref = head.get("ref") if isinstance(head, dict) else None
        state = item.get("state")
        if base_repo == args.repository and head_ref == branch and state == "open":
            matching.append(item)

    if matching:
        numbers = ",".join(str(item.get("number")) for item in matching)
        stop(
            f"conflicting open PR exists for head branch {branch}: PR(s) {numbers}",
            EXIT_CONFLICTING_PR,
        )

    print("PR_STATE_GATE=PASS")
    print(f"repository={args.repository}")
    print(f"head_branch={branch}")
    print("open_prs=0")


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify GitHub PR state.")
    parser.add_argument("--repository", required=True)
    parser.add_argument("--fixture", help="Offline JSON fixture instead of live GitHub API.")

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--pr-number", type=int)
    mode.add_argument("--expect-no-open-pr-for-head")

    parser.add_argument("--expected-head")
    parser.add_argument("--expected-base")
    parser.add_argument("--expected-state", default="open")
    args = parser.parse_args()

    if not REPOSITORY_RE.fullmatch(args.repository):
        stop("repository must use owner/name form", 2)

    if args.pr_number is not None:
        verify_specific_pr(args)
    else:
        verify_no_open_pr(args)


if __name__ == "__main__":
    main()
